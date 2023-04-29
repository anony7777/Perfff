#include <sstream>
#include <string>

#include "clang/AST/AST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/ASTConsumers.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "llvm/Support/raw_ostream.h"
#include "clang/Rewrite/Core/Rewriter.h"

using namespace clang;
using namespace clang::driver;
using namespace clang::tooling;
using namespace std;

static llvm::cl::OptionCategory GNNToolCategory("GNN source-to-source tool");
const string tool_type = "dgl";     //dgl, pyg
const bool dgl_minibatch = true;    //dgl的minibatch
static int dgl_num_blocks=0;

// By implementing RecursiveASTVisitor, we can specify which AST nodes
// we're interested in by overriding relevant methods.
class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
private:
  Rewriter &TheRewriter;
  Rewriter::RewriteOptions opt;

  //在SL位置插入str（原SL位置的字符，在插入文本之后）
  void insertText(SourceLocation SL, string str) {
    TheRewriter.InsertText(SL, str, true, true);
  }
  //从SL位置开始，删除n个字符
  void removeText(SourceLocation SL, int n) {
    TheRewriter.RemoveText(SL, n, opt);
  }

  //调试时使用，输出信息
  void print(string str) {
    llvm::outs() << str;
  }
  void print(char c) {
    llvm::outs() << c;
  }
  void print(int n) {
    llvm::outs() << n;
  }

  //得到当前位置的字符
  char getChar(SourceLocation SL) {
    return TheRewriter.getRewrittenText(SourceRange(SL, SL.getLocWithOffset(1)))[0];
  }

  //得到当前位置开始的、长为<n>的字符串(得到的字符串长度>=n,)
  string getString(SourceLocation SL, int n) {  //n-string length
    return TheRewriter.getRewrittenText(SourceRange(SL, SL.getLocWithOffset(n+1)));
  }

  //跳过连续的空字符
  //SL为空字符' '，返回的SL为下一个非空字符的位置
  SourceLocation skipBlank(SourceLocation SL) {
    while (getChar(SL) == ' ')
      SL = SL.getLocWithOffset(1);
    return SL;
  }

  //找到下一个字符c的位置，自动跳过括号范围()
  //SL不为'('
  SourceLocation findChar(SourceLocation SL, char c) {  //not start from a specific left bracket
    int bracket = 0;  //括号层数
    char t;
    while ((t = getChar(SL)) != c || bracket != 0) 
    {
      if (t == '(')
        bracket++;
      else if (t == ')')
        bracket--;
      SL = SL.getLocWithOffset(1);
    }
    return SL;
  }
  //额外返回从当前SL到目标SL的距离count
  SourceLocation findChar(SourceLocation SL, char c, int& count) {  //not start from a specific left bracket
    int bracket = 0;  //括号层数
    count=0;
    char t;
    while ((t = getChar(SL)) != c || bracket != 0) 
    {
      if (t == '(')
        bracket++;
      else if (t == ')')
        bracket--;
      SL = SL.getLocWithOffset(1);
      count++;
    }
    return SL;
  }

  //找到与当前'('匹配的')'的位置
  //SL为'('的位置
  SourceLocation findRightBracket(SourceLocation SL) {
    if (getChar(SL) != '(')
    {
      print("[findRightBracket error]: SL isn't \'(\'\n");
      return SL;
    }

    int bracket = 1;
    SL = SL.getLocWithOffset(1);  //(
    char t = getChar(SL);
    while (bracket != 0) {
      if (t == '(')
        bracket++;
      else if (t == ')')
        bracket--;
      SL = SL.getLocWithOffset(1);
      t = getChar(SL);
    }
    return SL.getLocWithOffset(-1);
  }

  //得到函数调用时实参的个数
  //SL为函数调用'('的位置
  int getActualParamNum(SourceLocation SL) {
    if (getChar(SL) != '(')
    {
      print("[getActualParamNum error]: SL isn't \'(\'\n");
      return 0;
    }

    SL = SL.getLocWithOffset(1);  //跳过'('
    SL = skipBlank(SL);
    if (getChar(SL) == ')') //没有实参
      return 0;

    int bracket = 1;
    int num_param = 1;  //初始时有1个参数，之后一个','增加1个参数
    char t = getChar(SL);
    while (bracket != 0) {
      if (t == '(')
        bracket++;
      else if (t == ')')
        bracket--;
      else if (bracket ==1 && t == ',')
        num_param++;
      SL = SL.getLocWithOffset(1);
      t = getChar(SL);
    }
    return num_param;
  }

public:
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}

  //★类内成员调用，如类内变量、类内方法
  //Structure and Union Members
  bool VisitMemberExpr(MemberExpr *p) {
    string type = p->getMemberDecl()->getType().getAsString();
    string name = p->getFoundDecl().getDecl()->getNameAsString();
    //insertText(p->getMemberLoc(), "<MemberExpr><"+type+">"+"<"+name+">");
    SourceLocation SL_begin = p->getMemberLoc();
    if (name == "forward")
    {
      SourceLocation SL_forward = SL_begin.getLocWithOffset(-1);
      int delete_n = 8; //默认删除".forward"共8个字符
      while (getChar(SL_forward) != '.')  //考虑".  forward"的情况
      {
        delete_n++;
        SL_forward = SL_forward.getLocWithOffset(-1);
      }

      //forward(g, h) 改成 forward(h, g.edge_index)
      if (tool_type == "pyg" && type == "tensor (Graph, tensor)") //GCNConv GATConv GINConv SAGEConv
      {
        SourceLocation SL = skipBlank(SL_begin).getLocWithOffset(7); //forward
        SL = skipBlank(SL).getLocWithOffset(1); // (
        SourceLocation SL_param1 = SL; //第1个参数g的起始位置
        string name_param1 = getString(SL_param1, 1); //此时得到的可能为"g, "
        while (name_param1[name_param1.length()-1] == ',' || name_param1[name_param1.length()-1] == ' ')
          name_param1 = name_param1.substr(0, name_param1.length()-1);
        int count=0;  //从SL_param1开始删除第1个参数，需要删除的字符个数
        SL = findChar(SL, ',', count);

        SL = SL.getLocWithOffset(1);  //,
        count++;
        while (getChar(SL) == ' ')
        {
          SL = SL.getLocWithOffset(1);
          count++;
        }

        while (getChar(SL) != ' ' && getChar(SL) != ')')  //跳过第2个参数
          SL = SL.getLocWithOffset(1);

        insertText(SL, ", " + name_param1 + ".edge_index");
        //最后删除第1个参数
        removeText(SL_param1, count);
      }
      else if (tool_type == "dgl" && dgl_minibatch && type == "tensor (Graph, tensor)")
      {
        SourceLocation SL = skipBlank(SL_begin).getLocWithOffset(7); //forward
        SL = skipBlank(SL).getLocWithOffset(1); // (
        SL = skipBlank(SL);
        while (getChar(SL) != ' ' && getChar(SL) != ',')  //g
          SL = SL.getLocWithOffset(1);
        insertText(SL, "[" + to_string(dgl_num_blocks++) + "]");
      }

      //最后删除在前的forward
      removeText(SL_forward, delete_n);  //.forward
    }
    //处理Graph.node_feat
    else if (name == "node_feat")
    {
      //删除node_feat()
      SourceLocation SL = SL_begin.getLocWithOffset(9);
      int n = 9;  //要删除的长度
      while (getChar(SL) == ' ')
      {
        SL = SL.getLocWithOffset(1);
        n++;
      }
      SL = SL.getLocWithOffset(1);  //(
      n++;
      while (getChar(SL) != ')')
      {
        SL = SL.getLocWithOffset(1);
        n++;
      }
      n++;  //)
      removeText(SL_begin, n);

      if (tool_type == "dgl")
        insertText(SL_begin, "ndata[\'feat\']");
      else
        insertText(SL_begin, "x");
    }
    return true;
  }

  //★
  //函数引用指针
  //A reference to a declared variable, function, enum
  bool VisitDeclRefExpr(DeclRefExpr *p) {
    //string type = p->getDecl()->getType().getAsString();
    string name = p->getFoundDecl()->getNameAsString();
    if (name == "super") 
    {
      SourceLocation SL = p->getBeginLoc();
      insertText(SL.getLocWithOffset(5), "().__init__");
    }
    else if (name.substr(0, 6) == "utils_") //把"untils_"改为"utils."
    {
      SourceLocation SL = p->getBeginLoc().getLocWithOffset(5); //utils
      removeText(SL, 1);
      insertText(SL, ".");
    }
    else if (name == "Readout_nodes")
    {
      SourceLocation SL_begin = p->getBeginLoc();
      if (tool_type == "dgl")
      {
        //Readout_nodes(batch, h) 改为:
        //with g.local_scope():
        //    g.ndata['h'] = h
        //    h = dgl.mean_nodes(g, 'h')

        //得到2个参数名
        SourceLocation SL = skipBlank(SL_begin).getLocWithOffset(13); //Readout_nodes
        SL = skipBlank(SL).getLocWithOffset(1); // (
        SL = skipBlank(SL);
        string name_param1 = getString(SL, 1); //第1个参数的名  <batch>
        while (name_param1[name_param1.length()-1] == ',' || name_param1[name_param1.length()-1] == ' ')
          name_param1 = name_param1.substr(0, name_param1.length()-1);
        
        SL = findChar(SL, ',');
        SL = SL.getLocWithOffset(1);  //,
        SL = skipBlank(SL);
        string name_param2 = getString(SL, 1); //第2个参数的名 可能为"h);" "h )"  <h>
        while (name_param2[name_param2.length()-1] == ')' || name_param2[name_param2.length()-1] == ';' || name_param2[name_param2.length()-1] == ' ')
          name_param2 = name_param2.substr(0, name_param2.length()-1);

        //insertText(SL_begin, "<"+name_param1+"><"+name_param2+">");

        int count_SL_begin;  //从SL_begin开始删除该行需要删除的字符数
        findChar(SL_begin, ';', count_SL_begin);

        //找到 <here>h = 
        SL = SL_begin;
        int count_SL = 0;  //从目标SL开始删除，需要删除的字符数
        while (getChar(SL) != '=')
        {
          print(getChar(SL));
          SL = SL.getLocWithOffset(-1);
          count_SL++;
        }
        SL = SL.getLocWithOffset(-1); //=
        count_SL++;
        while (getChar(SL) == ' ')
        {
          SL = SL.getLocWithOffset(-1);
          count_SL++;
        }
        while (getChar(SL) != ' ' && getChar(SL) != '\n' && getChar(SL) != '\t')
        {
          SL = SL.getLocWithOffset(-1);
          count_SL++;
        }
        SL = SL.getLocWithOffset(1);
        count_SL--;

        removeText(SL_begin, count_SL_begin);  //删除Readout_nodes(batch, h);
        removeText(SL, count_SL);        //删除h = 
        
        insertText(SL_begin, "with " + name_param1 + ".local_scope():\n" + name_param1 + ".ndata[\'" + name_param2 + "\'] = " + name_param2 + "\n" + name_param2 + " = dgl.mean_nodes(" + name_param1 + ", \'" + name_param2 + "\')");
      }
      else  //pyg
      {
        //Readout_nodes(batch, h) 改为 torch_geometric.nn.global_mean_pool(h, batch)

        //只有2个参数的函数：交换2个参数的位置
        SourceLocation SL = skipBlank(SL_begin).getLocWithOffset(13); //Readout_nodes
        SL = skipBlank(SL).getLocWithOffset(1); // (
        SourceLocation SL_param1 = SL; //第1个参数g的起始位置
        string name_param1 = getString(SL_param1, 1); //第1个参数的名
        while (name_param1[name_param1.length()-1] == ',' || name_param1[name_param1.length()-1] == ' ')
          name_param1 = name_param1.substr(0, name_param1.length()-1);
        
        int count=0;  //从SL_param1开始删除第1个参数，需要删除的字符个数

        SL = findChar(SL, ',', count);
        SL = SL.getLocWithOffset(1);  //,
        count++;
        while (getChar(SL) == ' ')
        {
          SL = SL.getLocWithOffset(1);
          count++;
        }

        while (getChar(SL) != ' ' && getChar(SL) != ')')  //跳过第2个参数
          SL = SL.getLocWithOffset(1);

        insertText(SL, ", " + name_param1 + ".batch");
        //最后删除第1个参数
        removeText(SL_param1, count);

        removeText(SL_begin, 13); //删除Readout_nodes
        insertText(SL_begin, "torch_geometric.nn.global_mean_pool");
      }
    }
    else if (name == "init_xavier_normal_")
    {
      SourceLocation SL = p->getBeginLoc();
      removeText(SL, name.length());
      insertText(SL, "nn.init.xavier_uniform_");
    }
    else if (name == "add_pool")
    {
      SourceLocation SL_begin = p->getBeginLoc();
      if (tool_type == "dgl")
      {
        removeText(SL_begin, 8);  //add_pool
        insertText(SL_begin, "sumpool");

        SourceLocation SL = SL_begin.getLocWithOffset(-1);
        while (getChar(SL) == ' ')
          SL = SL.getLocWithOffset(-1);
        SL = SL.getLocWithOffset(-1); //=
        while (getChar(SL) == ' ')
          SL = SL.getLocWithOffset(-1);
        while (getChar(SL) != ' ' && getChar(SL) != '\n' && getChar(SL) != '\t')
          SL = SL.getLocWithOffset(-1);
        insertText(SL.getLocWithOffset(1), "sumpool=dgl.nn.pytorch.glob.SumPooling()\n");
      }
      else  //pyg
      {
        SourceLocation SL = SL_begin.getLocWithOffset(8); //add_pool
        SL = skipBlank(SL);
        SL = SL.getLocWithOffset(1);  //(
        SL = skipBlank(SL);
        SourceLocation SL_param1 = SL;
        string name_param1 = getString(SL_param1, 1);  //g
        while (name_param1[name_param1.length()-1] == ',' || name_param1[name_param1.length()-1] == ' ')
          name_param1 = name_param1.substr(0, name_param1.length()-1);
        
        int count=0;
        SL = findChar(SL, ',', count);
        SL = SL.getLocWithOffset(1);  //,
        count++;
        while (getChar(SL) == ' ')
        {
          SL = SL.getLocWithOffset(1);
          count++;
        } //此时SL为param2
        while (getChar(SL) != ' ' && getChar(SL) != ')')
          SL = SL.getLocWithOffset(1);

        insertText(SL, ", " + name_param1 + ".batch");
        removeText(SL_param1, count); //g, 
        removeText(SL_begin, 8);  //add_pool
        insertText(SL_begin, "torch_geometric.nn.global_add_pool");
      }
    }
    return true;
  }

  //★CXXTemporaryObjectExpr和CXXFunctionalCastExpr都是调用构造器，不同的构造函数会被分配到这两个其中一个
  //统一为构造器分析
  void VisitConstructorExpr(SourceLocation SL_begin, string type) {
    if (type == "GCNConv")
    {
      SourceLocation SL = SL_begin.getLocWithOffset(7); //GCNConv
      while (getChar(SL) != '(') SL = SL.getLocWithOffset(1); //将SL指向'('
      if (getActualParamNum(SL) > 2) 
      {
        SL = SL.getLocWithOffset(1);  //(
        SL = findChar(SL, ',');       //in_dim
        SL = SL.getLocWithOffset(1);  //,
        SL = findChar(SL, ',');       //out_dim
        SL = SL.getLocWithOffset(1);  //,
        SL = skipBlank(SL);
        SourceLocation SL_bias = SL;
        SL = findChar(SL, ',');       //bias
        SL = SL.getLocWithOffset(1);  //,
        SL = skipBlank(SL);
        SourceLocation SL_normalize = SL;
        while (getChar(SL) != ' ' && getChar(SL) != ')')
          SL = SL.getLocWithOffset(1);
        SourceLocation SL_selfloop = SL;

        if (tool_type == "dgl") 
        {
          insertText(SL_selfloop, ", allow_zero_in_degree=True");
          //dgl的norm: 'both' / 'none'
          if (getString(SL_normalize, 1) == "true")
          {
            removeText(SL_normalize, 4);
            insertText(SL_normalize, "norm=\'both\'");
          }
          else  //"false"
          {
            removeText(SL_normalize, 5);
            insertText(SL_normalize, "norm=\'none\'");
          }

          insertText(SL_bias, "bias=");
        } 
        else  //pyg
        {
          //insertText(SL_selfloop, ", add_self_loops=True"); //pyg add_self_loop
          insertText(SL_normalize, "normalize=");
          insertText(SL_bias, "bias=");
        }
      }
      else  //getActualParamNum(SL) == 2
      {
        if (tool_type == "dgl")
        {
          SourceLocation SL = SL_begin.getLocWithOffset(7); //GCNConv
          while (getChar(SL) != '(')  //将SL指向'('
            SL = SL.getLocWithOffset(1);
          SL = SL.getLocWithOffset(1);  //(
          SL = findChar(SL, ',');       //in_dim
          SL = SL.getLocWithOffset(1);  //,
          SL = skipBlank(SL);
          while (getChar(SL) != ' ' && getChar(SL) != ')')    //out_dim
            SL = SL.getLocWithOffset(1);
          insertText(SL, ", allow_zero_in_degree=True");
        }
        //pyg add_self_loop
        /*if (tool_type == "pyg")
        {
          SourceLocation SL = SL_begin.getLocWithOffset(7); //GCNConv
          while (getChar(SL) != '(')  //将SL指向'('
            SL = SL.getLocWithOffset(1);
          SL = SL.getLocWithOffset(1);  //(
          SL = findChar(SL, ',');       //in_dim
          SL = SL.getLocWithOffset(1);  //,
          SL = skipBlank(SL);
          while (getChar(SL) != ' ' && getChar(SL) != ')')    //out_dim
            SL = SL.getLocWithOffset(1);
          insertText(SL, ", add_self_loops=True");
        }*/
      }

      if (tool_type == "dgl") 
      {
        removeText(SL_begin, type.length());
        insertText(SL_begin, "GraphConv");
      }
    } 
    else if (type == "SAGEConv") 
    {
      SourceLocation SL = SL_begin.getLocWithOffset(8); //SAGEConv
      while (getChar(SL) != '(') SL = SL.getLocWithOffset(1); //将SL指向'('
      if (getActualParamNum(SL) > 2) 
      {
        SL = SL.getLocWithOffset(1);  //(
        SL = findChar(SL, ',');       //in_dim
        SL = SL.getLocWithOffset(1);  //,
        SL = findChar(SL, ',');       //out_dim
        SL = SL.getLocWithOffset(1);  //,
        SL = skipBlank(SL);
        SourceLocation SL_aggregator_type = SL;
        string aggr_value = getString(SL_aggregator_type, 1); //得到为 <"max> <"mean> <"add> <"lstm>
        aggr_value = aggr_value.substr(1);
        SL = findChar(SL, ',');       //aggregator_type
        SL = SL.getLocWithOffset(1);  //,
        SL = skipBlank(SL);
        SourceLocation SL_bias = SL;

        if (tool_type == "dgl")
        {
          insertText(SL_bias, "bias=");

          removeText(SL_aggregator_type, aggr_value.length()+2);
          insertText(SL_aggregator_type, "aggregator_type=");
          if (aggr_value == "add")
            insertText(SL_aggregator_type, "\'gcn\'");
          else if (aggr_value == "max")
            insertText(SL_aggregator_type, "\'pool\'");
          else if (aggr_value == "mean")
            insertText(SL_aggregator_type, "\'mean\'");
          else  //lstm
            insertText(SL_aggregator_type, "\'lstm\'");
        }
        else  //pyg
        {
          insertText(SL_bias, "bias=");
          
          removeText(SL_aggregator_type, aggr_value.length()+2);
          insertText(SL_aggregator_type, "aggr=");
          if (aggr_value == "add")
            insertText(SL_aggregator_type, "\'add\'");
          else if (aggr_value == "max")
            insertText(SL_aggregator_type, "\'max\'");
          else if (aggr_value == "mean")
            insertText(SL_aggregator_type, "\'mean\'");
          else  //lstm
            insertText(SL_aggregator_type, "\'lstm\'");
        }
      }
      else {  //getActualParamNum(SL) <= 2
        if (tool_type == "dgl")  //DGL:在参数最后，加上一个,'mean' 以对齐pyg的默认
        {
          SourceLocation SL = SL_begin;
          while (getChar(SL) != ';') SL = SL.getLocWithOffset(1);
          while (getChar(SL) != ')') SL = SL.getLocWithOffset(-1);
          insertText(SL, ", \'mean\'");
        }
      }
    } 
    else if (type == "GATConv") 
    {
      SourceLocation SL = SL_begin.getLocWithOffset(7); //GATConv
      while (getChar(SL) != '(') SL = SL.getLocWithOffset(1); ////将SL指向'('

      bool has_bias = false;
      if (getActualParamNum(SL) > 5)
        has_bias = true;
      
      SL = SL.getLocWithOffset(1);  //(
      SL = findChar(SL, ',');       //in_dim
      SL = SL.getLocWithOffset(1);  //,
      SL = findChar(SL, ',');       //out_dim
      SL = SL.getLocWithOffset(1);  //,
      SL = skipBlank(SL);
      SourceLocation SL_heads = SL;
      SL = findChar(SL, ',');       //heads
      SL = SL.getLocWithOffset(1);  //,
      SL = skipBlank(SL);
      SourceLocation SL_attn_drop = SL;
      SL = findChar(SL, ',');       //attn_drop
      SL = SL.getLocWithOffset(1);  //,
      SL = skipBlank(SL);
      SourceLocation SL_negative_slope = SL;
      SourceLocation SL_bias;
      if (has_bias)
      {
        SL = findChar(SL, ',');
        SL = SL.getLocWithOffset(1);  //,
        SL = skipBlank(SL);
        SL_bias = SL;
      }
      while (getChar(SL) != ' ' && getChar(SL) != ')')
          SL = SL.getLocWithOffset(1);
      SourceLocation SL_selfloop = SL;

      if (tool_type == "dgl") 
      {
        insertText(SL_selfloop, ", allow_zero_in_degree=True");
        if (has_bias)
          insertText(SL_bias, "bias=");
        insertText(SL_negative_slope, "negative_slope=");
        insertText(SL_attn_drop, "attn_drop=");
        insertText(SL_heads, "num_heads=");
      } 
      else  //pyg
      {
        SL = findChar(SL, ')');
        insertText(SL, ", add_self_loops=True");
        if (has_bias)
          TheRewriter.InsertText(SL_bias, "bias=", true, true);
        insertText(SL_negative_slope, "negative_slope=");
        insertText(SL_attn_drop, "dropout=");
        insertText(SL_heads, "heads=");
      }
    } 
    else if (type == "GINConv") 
    {
      SourceLocation SL = SL_begin.getLocWithOffset(7); //GINConv
      while (getChar(SL) != '(') SL = SL.getLocWithOffset(1); //将SL指向'('
      SL = SL.getLocWithOffset(1);  //(
      SL = skipBlank(SL);
      SourceLocation SL_node_func = SL;
      SL = findChar(SL, ',');       //node_func
      SL = SL.getLocWithOffset(1);  //,
      SL = skipBlank(SL);
      SourceLocation SL_eps = SL;
      SL = findChar(SL, ',');       //eps
      SL = SL.getLocWithOffset(1);  //,
      SL = skipBlank(SL);
      SourceLocation SL_train_eps = SL;

      if (tool_type == "dgl") 
      {
        insertText(SL_train_eps, "learn_eps=");
        insertText(SL_eps, "init_eps=");
        insertText(SL_node_func, "aggregator_type=\'sum\', apply_func=");
      } 
      else  //pyg
      {
        insertText(SL_train_eps, "train_eps=");
        insertText(SL_eps, "eps=");
        insertText(SL_node_func, "nn=");
      }
    } 
    else if (type == "Dropout" || type == "LeakyReLU" || type == "ReLU" || type == "Tanh" || type == "ELU" || type == "Linear" ||
             type == "BatchNorm1d") 
    {
      insertText(SL_begin, "nn.");
    }
  }

  //☆变量定义
  //删除变量定义前的类型，使符合python语法
  bool VisitVarDecl(VarDecl *p) {
    SourceLocation SL_begin = p->getBeginLoc();
    string type = p->getType().getAsString();
    if (type == "tensor" || type == "int" || type == "Graph" || type == "Activation" || type == "double" || type == "float")
    {
      //去除多余空格
      int n = type.length()+1;
      SourceLocation SL = SL_begin.getLocWithOffset(n);
      while (getChar(SL) == ' ')
      {
        n++;
        SL = SL.getLocWithOffset(1);
      }
      removeText(SL_begin, n);
    }
    return true;
  }

  //构造器：临时变量
  //Represents a C++ functional cast expression that builds a temporary object
  bool VisitCXXTemporaryObjectExpr(CXXTemporaryObjectExpr *p) { //constructer has more than 1 parameter
    //insertText(SL_begin, "<Temporary><"+type+">");
    VisitConstructorExpr(p->getBeginLoc(), p->getTypeSourceInfo()->getType().getAsString());
    return true;
  }

  //构造器
  bool VisitCXXFunctionalCastExpr(CXXFunctionalCastExpr *p) {
    //insertText(SL_begin, "<FunctionalCast><"+type+">");
    VisitConstructorExpr(p->getBeginLoc(), p->getTypeAsWritten().getAsString());
    return true;
  }

  //class/struct/union定义（这里只用到class）
  //在类定义括号内添加nn.module                                                                                                                                          
  bool VisitCXXRecordDecl(CXXRecordDecl *p) {
    SourceLocation SL = p->getInnerLocStart().getLocWithOffset(6);  //跳过"class "
    SL = skipBlank(SL);
    SL = SL.getLocWithOffset(p->getNameAsString().length());
    insertText(SL, "(nn.Module):");
    return true;
  }

  //class/struct/union定义的方法定义
  //只对涉及到的函数进行处理，删除无用的函数声明
  bool VisitCXXMethodDecl(CXXMethodDecl *p) {
    string func_name = p->getNameAsString(); //函数名
    if (p->hasBody() && (func_name == "__init__" || func_name == "forward"))
    {
      SourceLocation SL_func_begin = p->getSourceRange().getBegin(); //函数定义开始位置
      int type_length = p->getDeclaredReturnType().getAsString().length();  //返回值类型的字符串长度
      
      int formal_param_num = p->param_size();       //函数形参个数
      SourceLocation SL_formal_param_begin = SL_func_begin.getLocWithOffset(type_length); //指向函数形参的'('
      SL_formal_param_begin = skipBlank(SL_formal_param_begin).getLocWithOffset(func_name.length());  //跳过空格和函数名
      SL_formal_param_begin = skipBlank(SL_formal_param_begin); //跳过空格
      SourceLocation SL_formal_param_end = findRightBracket(SL_formal_param_begin); //指向函数形参的')'

      //插入python函数定义的':'
      insertText(SL_formal_param_end.getLocWithOffset(1), ":");

      //增加self / self, 
      if (formal_param_num > 0)
        insertText(SL_formal_param_begin.getLocWithOffset(1), "self, ");
      else
        insertText(SL_formal_param_begin.getLocWithOffset(1), "self");

      //删除方法的返回值类型，增加'def'
      removeText(SL_func_begin, type_length);
      insertText(SL_func_begin, "def");
    }
    return true;
  }

  //修改"this->"为"self."
  bool VisitCXXThisExpr(CXXThisExpr *p) {
    SourceLocation SL = p->getSourceRange().getBegin();
    if (getString(SL, 3) == "this->")
      removeText(SL, 6);
    insertText(SL, "self.");
    return true;
  }
};

// Implementation of the ASTConsumer interface for reading an AST produced
// by the Clang parser.
class MyASTConsumer : public ASTConsumer {
public:
  MyASTConsumer(Rewriter &R) : Visitor(R) {}

  // Override the method that gets called for each parsed top-level
  // declaration.
  bool HandleTopLevelDecl(DeclGroupRef DR) override {
    for (DeclGroupRef::iterator b = DR.begin(), e = DR.end(); b != e; ++b) {
      // Traverse the declaration using our AST visitor.
      Visitor.TraverseDecl(*b);
      //输出结构信息
      //(*b)->dump();
    }
    return true;
  }

private:
  MyASTVisitor Visitor;
};

// For each source file provided to the tool, a new FrontendAction is created.
class MyFrontendAction : public ASTFrontendAction {
public:
  MyFrontendAction() {}

  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI,
                                                 StringRef file) override {
    //llvm::errs() << "** Creating AST consumer for: " << file << "\n";
    TheRewriter.setSourceMgr(CI.getSourceManager(), CI.getLangOpts());
    return std::make_unique<MyASTConsumer>(TheRewriter);
  }
  
  void EndSourceFileAction() override {
    SourceManager &SM = TheRewriter.getSourceMgr();
    //llvm::errs() << "** EndSourceFileAction for: " << SM.getFileEntryForID(SM.getMainFileID())->getName() << "\n";

    // Now emit the rewritten buffer.
    TheRewriter.getEditBuffer(SM.getMainFileID()).write(llvm::outs());
  }

private:
  Rewriter TheRewriter;
};

int main(int argc, const char **argv) {
  auto ExpectedParser = CommonOptionsParser::create(argc, argv, GNNToolCategory);
  if (!ExpectedParser) {
    llvm::errs() << ExpectedParser.takeError();
    return 1;
  }
  
  CommonOptionsParser& op = ExpectedParser.get();
  ClangTool Tool(op.getCompilations(), op.getSourcePathList());

  return Tool.run(newFrontendActionFactory<MyFrontendAction>().get());
}

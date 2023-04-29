# 使用方式：放在llvm-project/目录下   ./compile.sh
# $1: dgl/pyg/[both]

if [ $1 = "dgl" ];then
    sed -i 's/pyg/dgl/g' /home/mkj/llvm-project/clang/tools/code-transformer/CMakeLists.txt
    sed -i 's/d-minibatch/dgl/g' /home/mkj/llvm-project/clang/tools/code-transformer/CMakeLists.txt
    sed -i 's/const string tool_type = \"pyg\";/const string tool_type = \"dgl\";/g' /home/mkj/llvm-project/clang/tools/code-transformer/code-transformer.cpp
    sed -i 's/const bool dgl_minibatch = true;/const bool dgl_minibatch = false;/g' /home/mkj/llvm-project/clang/tools/code-transformer/code-transformer.cpp
    cd /home/mkj/llvm-project/build/tools/clang/tools/code-transformer/
    make
elif [ $1 = "pyg" ];then
    sed -i 's/dgl/pyg/g' /home/mkj/llvm-project/clang/tools/code-transformer/CMakeLists.txt
    sed -i 's/d-minibatch/pyg/g' /home/mkj/llvm-project/clang/tools/code-transformer/CMakeLists.txt
    sed -i 's/const string tool_type = \"dgl\";/const string tool_type = \"pyg\";/g' /home/mkj/llvm-project/clang/tools/code-transformer/code-transformer.cpp
    cd /home/mkj/llvm-project/build/tools/clang/tools/code-transformer/
    make
elif [ $1 = "dgl-minibatch" ];then
    sed -i 's/dgl/d-minibatch/g' /home/mkj/llvm-project/clang/tools/code-transformer/CMakeLists.txt
    sed -i 's/pyg/d-minibatch/g' /home/mkj/llvm-project/clang/tools/code-transformer/CMakeLists.txt
    sed -i 's/const string tool_type = \"pyg\";/const string tool_type = \"dgl\";/g' /home/mkj/llvm-project/clang/tools/code-transformer/code-transformer.cpp
    sed -i 's/const bool dgl_minibatch = false;/const bool dgl_minibatch = true;/g' /home/mkj/llvm-project/clang/tools/code-transformer/code-transformer.cpp
    cd /home/mkj/llvm-project/build/tools/clang/tools/code-transformer/
    make
else
    sed -i 's/pyg/dgl/g' /home/mkj/llvm-project/clang/tools/code-transformer/CMakeLists.txt
    sed -i 's/d-minibatch/dgl/g' /home/mkj/llvm-project/clang/tools/code-transformer/CMakeLists.txt
    sed -i 's/const string tool_type = \"pyg\";/const string tool_type = \"dgl\";/g' /home/mkj/llvm-project/clang/tools/code-transformer/code-transformer.cpp
    sed -i 's/const bool dgl_minibatch = true;/const bool dgl_minibatch = false;/g' /home/mkj/llvm-project/clang/tools/code-transformer/code-transformer.cpp
    cd /home/mkj/llvm-project/build/tools/clang/tools/code-transformer/
    make

    sed -i 's/dgl/pyg/g' /home/mkj/llvm-project/clang/tools/code-transformer/CMakeLists.txt
    sed -i 's/d-minibatch/pyg/g' /home/mkj/llvm-project/clang/tools/code-transformer/CMakeLists.txt
    sed -i 's/const string tool_type = \"dgl\";/const string tool_type = \"pyg\";/g' /home/mkj/llvm-project/clang/tools/code-transformer/code-transformer.cpp
    make

    sed -i 's/dgl/d-minibatch/g' /home/mkj/llvm-project/clang/tools/code-transformer/CMakeLists.txt
    sed -i 's/pyg/d-minibatch/g' /home/mkj/llvm-project/clang/tools/code-transformer/CMakeLists.txt
    sed -i 's/const string tool_type = \"pyg\";/const string tool_type = \"dgl\";/g' /home/mkj/llvm-project/clang/tools/code-transformer/code-transformer.cpp
    sed -i 's/const bool dgl_minibatch = false;/const bool dgl_minibatch = true;/g' /home/mkj/llvm-project/clang/tools/code-transformer/code-transformer.cpp
    make
fi

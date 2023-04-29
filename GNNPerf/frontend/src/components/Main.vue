<template>
  <div class="background-div">
    <v-container>   
      <v-card elevation="4" outlined>

        <!-- 导航栏 -->
        <v-row justify="center">
          <v-container>
            <v-row class="mx-4 mt-4 mb-0">
              <v-card-title>Choose a Project</v-card-title>
            </v-row>
            <v-row class="mx-4 my-0">

              <!-- 下拉选择框 -->
              <v-col cols="4">
                <v-select
                  v-model="selected_project"
                  :items="projects"
                  @change="fetchProject"
                ></v-select>
              </v-col>

              <!-- new project -->
              <v-col cols="2" class="text-center" align-self="center">
                <v-btn
                  elevation="3"
                  class="white--text"
                  color="blue lighten-1"
                  @click="newProject()"
                >
                  new project
                </v-btn>
              </v-col>

              <!-- rename project -->
              <v-col cols="2" class="text-center" align-self="center">
                <v-btn
                  elevation="3"
                  class="white--text"
                  color="blue lighten-1"
                  @click="renameOverlay()"
                >
                  rename project
                </v-btn>
              </v-col>

              <!-- save project -->
              <v-col cols="2" class="text-center" align-self="center">
                <v-btn
                  elevation="3"
                  class="white--text"
                  color="blue lighten-1"
                  @click="saveProject()"
                >
                  save project
                </v-btn>
              </v-col>

              <!-- delete project -->
              <v-col cols="2" class="text-center" align-self="center">
                <v-btn
                  elevation="3"
                  class="white--text"
                  color="red lighten-1"
                  @click="deleteProject()"
                >
                  delete project
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-row>

        <!-- 代码部分 -->
        <v-row justify="center" class="mb-0">
          <!-- GUL -->
          <v-col cols="6">
            <v-container>
              <v-textarea
                :disabled="selected_project===''"
                outlined
                name="input-7-4"
                height="500"
                label="GUL"
                placeholder="define a GNN model with GUL..."
                v-model="codes.GUL"
              ></v-textarea>
            </v-container>
          </v-col>

          <!-- Utils -->
          <v-col cols="6">
            <v-container>
              <v-textarea
                :disabled="selected_project===''"
                outlined
                name="input-7-4"
                height="500"
                label="Utils"
                placeholder="define utils with PyTorch..."
                v-model="codes.utils"
              ></v-textarea>
            </v-container>
          </v-col>
        </v-row>
      </v-card>

      <v-row class="mx-4 mt-4 mb-2">
        <v-col align="center">
          <v-btn
            elevation="3"
            class="white--text"
            color="blue lighten-1"
            @click="compile()"
          >
            Compile GUL
          </v-btn>
        </v-col>
      </v-row>

      <br />

      <!-- DGL and PyG codes -->
      <v-row>
        <v-col cols="6">
          <v-card color="grey lighten-5" flat height="400px" tile elevation="8">
            <v-toolbar color="indigo lighten-3" dense>
              <v-app-bar-nav-icon></v-app-bar-nav-icon>

              <v-toolbar-title>DGL</v-toolbar-title>

              <v-spacer></v-spacer>

              <v-btn icon>
                <v-icon>mdi-download</v-icon>
              </v-btn>

              <v-btn icon>
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </v-toolbar>

            <pre v-highlightjs="codes.dgl"><code class="python code-highlight"></code></pre>
          </v-card>
        </v-col>
        <v-col cols="6">
          <v-card color="grey lighten-4" flat height="400px" tile elevation="8">
            <v-toolbar color="indigo lighten-3" dense>
              <v-app-bar-nav-icon></v-app-bar-nav-icon>

              <v-toolbar-title>PyG</v-toolbar-title>

              <v-spacer></v-spacer>

              <v-btn icon>
                <v-icon>mdi-download</v-icon>
              </v-btn>

              <v-btn icon>
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </v-toolbar>
            <pre v-highlightjs="codes.pyg"><code class="python code-highlight"></code></pre>
            <!--<vue-code-highlight language=“python”><pre v-highlightjs="codes.pyg"></pre></vue-code-highlight>-->
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <br />
      </v-row>
      <v-row>
        <v-col align="center">
          <v-btn
            :disabled="!ready_to_train"
            elevation="3"
            class="white--text"
            color="blue lighten-1"
            @click="train_set()"
          >
            Ready to train
          </v-btn>
        </v-col>
      </v-row>
      <v-row>
        <br />
      </v-row>
    </v-container>

    <!-- rename overlay -->
    <v-overlay class="my-overlay" :z-index="zIndex" :value="overlay_rename">
      <v-row justify="center">
        <v-card class="mx-auto" width="650" color="rgba(13, 59, 114, 0.4)" outlined hover>
          <v-container fluid>
            <v-col cols="12" align="center">
              <v-textarea
                outlined
                name="input-7-4"
                height="50"
                label="project name"
                placeholder="rename the project"
                v-model="project_rename"
              ></v-textarea>
            </v-col>
            <v-col cols="12" align="center">
              <v-btn
                elevation="3"
                class="white--text"
                color="blue lighten-1"
                @click="renameProject()"
              >
                rename project
              </v-btn>
            </v-col>
          </v-container>
        </v-card>
      </v-row>
    </v-overlay>

    <!-- train set overlay -->
    <v-overlay class="my-overlay" :z-index="zIndex" :value="overlay_train_setting">
      <v-row justify="center">
        <v-card class="mx-auto" width="650" color="rgba(13, 59, 114, 0.4)" outlined hover>
          <v-container fluid>
            <v-row>
              <v-col cols="12">
                <v-container>

                  <v-row>
                    <v-overflow-btn
                      class="mt-2"
                      :items="tasks"
                      label="GNN Task"
                      v-model="selected_task"
                    >
                    </v-overflow-btn>
                  </v-row>

                  <v-row>
                    <v-overflow-btn
                      class="mb-2"
                      :items="computedItems"
                      label="Dataset"
                      v-model="selected_dataset"
                    >
                    </v-overflow-btn>
                  </v-row>

                  <v-row>
                    <v-col cols="2" align="center">
                      <v-label style="color: white;">Epoches</v-label>
                    </v-col>
                    <v-col cols="10" align="center">
                      <v-slider
                        v-model="epoch"
                        class="align-center"
                        :max="epoch_max"
                        :min="epoch_min"
                        hide-details
                      >
                        <template v-slot:append>
                          <v-text-field
                            v-model="epoch"
                            class="mt-0 pt-0"
                            hide-details
                            single-line
                            type="number"
                            style="width: 60px"
                          ></v-text-field>
                        </template>
                      </v-slider>
                    </v-col>
                  </v-row>

                  <v-row>
                    <v-col cols="2" align="center">
                      <v-label style="color: white;">Minibatch size</v-label>
                    </v-col>
                    <v-col cols="10" align="center">
                      <v-slider
                        v-model="minibatch"
                        class="align-center"
                        :max="minibatch_max"
                        :min="minibatch_min"
                        hide-details
                      >
                        <template v-slot:append>
                          <v-text-field
                            v-model="minibatch"
                            class="mt-0 pt-0"
                            hide-details
                            single-line
                            type="number"
                            style="width: 60px"
                          ></v-text-field>
                        </template>
                      </v-slider>
                    </v-col>
                  </v-row>

                  <v-row>
                    <v-col cols="2" align="center">
                      <v-label style="color: white;">Layers</v-label>
                    </v-col>
                    <v-col cols="10" align="center">
                      <v-slider
                        v-model="layer"
                        class="align-center"
                        :max="layer_max"
                        :min="layer_min"
                        hide-details
                      >
                        <template v-slot:append>
                          <v-text-field
                            v-model="layer"
                            class="mt-0 pt-0"
                            hide-details
                            single-line
                            type="number"
                            style="width: 60px"
                          ></v-text-field>
                        </template>
                      </v-slider>
                    </v-col>
                  </v-row>
                </v-container>
              </v-col>
            </v-row>

            <!-- buttons -->
            <v-row>
              <v-col cols="6" align="center">
                <v-btn
                  :disabled="dialog"
                  :loading="dialog"
                  class="white--text"
                  rounded
                  text
                  elevation="3"
                  @click="train_start()"
                >
                  start
                </v-btn>
              </v-col>

              <v-col cols="6" align="center">
                <v-btn
                  :disabled="dialog"
                  :loading="dialog"
                  class="white--text"
                  rounded
                  text
                  elevation="3"
                  @click="train_cancel()"
                >
                  cancel
                </v-btn>
              </v-col>

              <v-dialog v-model="dialog" hide-overlay persistent width="300">
                <v-card color="green darken-3" dark>
                  <v-card-text>
                    Please stand by ...
                    <v-progress-linear
                      indeterminate
                      color="white"
                      class="mb-0"
                    ></v-progress-linear>
                  </v-card-text>
                </v-card>
              </v-dialog>
            </v-row>
          </v-container>
        </v-card>
      </v-row>
    </v-overlay>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "Main",

  components: {},

  data: () => ({
    urls: {
      fetchProjectNames: "/api/queryProjectNames/",
      fetchProject: "/api/queryProject/",
      newProject: "/api/newProject/",
      renameProject: "/api/renameProject/",
      saveProject: "/api/saveProject/",
      deleteProject: "/api/deleteProject/",
      compile: "/api/compile/",
      train: "/api/train/",

      genCodeBtnUrl: "/api/generateCode/",
      trainUrl: "/api/executeCode/",
      fetchAPIModels: "/api/queryAPIModels/",
    },
    projects: [], //项目名列表
    codes: {      //代码集合
      GUL: "",
      utils: "",
      dgl: "",
      pyg: ""
    },
    selected_project: "", //下拉选择框中选中的项目编号
    count: 1,
    project_rename: "",   //renameProject的name
    overlay_rename: false, //renameProject的dialog是否可视

    tasks: ["Node Classification", "Graph Classification"],
    selected_task: "",
    datasets_NC: ["pubmed", "ppi", "arxiv", "DD", "ddi", "colab", "ppa", "protein", "reddit.dgl"], 
    datasets_GC: ["MUTAG", "PROTEINS", "COLLAB"], 
    selected_dataset: "",
    
    epoch: 32,
    epoch_min: 1,
    epoch_max: 512,
    minibatch: 0,
    minibatch_min: 0,
    minibatch_max: 51200,
    layer: 1,
    layer_min: 1,
    layer_max: 16,

    dialog: false,  //training starting
    overlay_train_setting: false, //train setting
    ready_to_train: false
  }),

  computed: {
    computedItems () {
      if (this.selected_task === "Node Classification") {
        return this.datasets_NC
      } else if (this.selected_task === "Graph Classification") {
        return this.datasets_GC
      } else {
        return []
      }
    }
  },

  methods: {
    //初始化函数
    initial() {
      //this.$store.commit("setIsRoot", false);
      //this.user.uid = this.$store.state.loginUser.uname;
      this.fetchProjectNames();
    },

    //fetch项目名
    fetchProjectNames() {
      axios({
        method: "post",
        url: this.urls.fetchProjectNames
      })
        .then((res) => {
          this.projects = [];
          const names = Object.keys(res.data);
          this.count = 1;
          for (let name of names) {
            this.projects.push({value: this.count.toString(), text: name});
            this.count = this.count+1;
          }
        })
        .catch((err) => {
          console.log(err);
        });
    },

    //项目名和value值转换
    name2value(name) {
      let value = "";
      this.projects.forEach(function(project, index, array) {
        if (project.text.localeCompare(name) === 0) {
          value = project.value;
        }
      });
      return value;
    },
    value2name(value) {
      let name = "";
      this.projects.forEach(function(project, index, array) {
        if (project.value === value) {
          name = project.text;
        }
      });
      return name;
    },

    //fetch项目代码
    fetchProject() {
      var params = new URLSearchParams();
      params.append("project", this.value2name(this.selected_project));
      axios({
        method: "post",
        url: this.urls.fetchProject,
        data: params,
      })
        .then((res) => {
          this.codes.GUL = res.data.GUL;
          this.codes.utils = res.data.utils;
        })
        .catch((err) => {
          console.log(err);
        });
      this.ready_to_train = false;
    },

    //new project
    newProject() {
      var params = new URLSearchParams();
      axios({
        method: "post",
        url: this.urls.newProject
      })
        .catch((err) => {
          console.log(err);
        });

      this.fetchProjectNames();
      this.codes.GUL="";
      this.codes.utils="";
      this.codes.dgl="";
      this.codes.pyg="";
      this.ready_to_train = false;
    },

    //rename project()
    renameOverlay() {
      this.overlay_rename = true;
      this.project_rename = this.value2name(this.selected_project);
    },

    renameProject() {
      var params = new URLSearchParams();
      params.append("project_old", this.value2name(this.selected_project));
      params.append("project_new", this.project_rename);
      axios({
        method: "post",
        url: this.urls.renameProject,
        data: params,
      })
        .catch((err) => {
          console.log(err);
        });
      this.overlay_rename = false;
      this.fetchProjectNames();
      this.codes.GUL="";
      this.codes.utils="";
      this.codes.dgl="";
      this.codes.pyg="";
      this.ready_to_train = false;
    },

    //save project
    saveProject() {
      var params = new URLSearchParams();
      params.append("project", this.value2name(this.selected_project));
      params.append("GUL", this.codes.GUL);
      params.append("utils", this.codes.utils);
      axios({
        method: "post",
        url: this.urls.saveProject,
        data: params,
      })
        .catch((err) => {
          console.log(err);
        });
    },

    //delete project
    deleteProject() {
      var params = new URLSearchParams();
      params.append("project", this.value2name(this.selected_project));
      axios({
        method: "post",
        url: this.urls.deleteProject,
        data: params,
      })
        .catch((err) => {
          console.log(err);
        });
      
      this.fetchProjectNames();
      this.selected_project = "";
      this.codes.GUL="";
      this.codes.utils="";
      this.codes.dgl="";
      this.codes.pyg="";
      this.ready_to_train = false;
    },

    //compile
    compile() {
      this.saveProject();
      
      var params = new URLSearchParams();
      params.append("project", this.value2name(this.selected_project));
      axios({
        method: "post",
        url: this.urls.compile,
        data: params,
      })
        .then((res) => {
          this.codes.dgl = res.data.dgl;
          this.codes.pyg = res.data.pyg;
        })
        .catch((err) => {
          console.log(err);
        });
        this.ready_to_train = true;
    },

    //显示train setting overlay
    train_set() {
      this.overlay_train_setting = true;
    },

    //隐藏train setting overlay
    train_cancel() {
      this.overlay_train_setting = false;
    },

    //开始训练
    train_start() {
      this.dialog = true;
      var params = new URLSearchParams();
      params.append("project", this.value2name(this.selected_project));
      params.append("task", this.selected_task);
      params.append("dataset", this.selected_dataset);
      params.append("epoch", this.epoch);
      params.append("minibatch", this.minibatch);
      params.append("layer", this.layer);

      axios({
        method: "post",
        url: this.urls.train,
        data: params,
      })
        .catch((err) => {
          console.log(err);
        });
    }
  },

  watch: {
    dialog(val) { //页面跳转
      if (!val) {
        this.overlay = !this.overlay;
        this.$router.push("/resultlist/");
        return;
      }

      setTimeout(() => (this.dialog = false), 1000);
    }
  },

  //在页面启动时
  mounted() {
    this.initial();
  }
};
</script>

<style scoped>
@import url("../assets/css/helloworld.css");
@import url("../assets/css/public.css");
.my-overlay >>> .v-overlay__content {
  width: 100%;
  height: 100%;
  padding-top: 7%;
}

.h1,
h1 {
  text-align: center;
}
</style>

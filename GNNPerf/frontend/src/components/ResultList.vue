<template>
  <div class="background-div">
    <v-container>
      <v-card elevation="4" outlined>
        <v-container>
          <v-card-title>Results</v-card-title>

          <!-- Search -->
          <v-card-title>
            <v-text-field
              v-model="search"
              append-icon="mdi-magnify"
              label="Search"
              single-line
              hide-details
            ></v-text-field>
          </v-card-title>

          <!-- Tabel -->
          <!-- item-key设置不正确，会导致表格出问题 -->
          <v-data-table
            :headers="headers"
            :items="results"
            :search="search"
            item-key="key"
            class="elevation-5"
            ref="table"
            single-expand
            @click:row="(item, event) => {event.expand(!event.isExpanded); onRowClick(item);}"
          >
            <template v-slot:[`item.analyse`]="{ item }">
              <v-icon v-if="item.status === '1'" @click="viewResult(item)">
                mdi-pencil
              </v-icon>
              <v-progress-circular
                v-else
                color="green lighten-3"
                indeterminate
              ></v-progress-circular>
            </template>

            <template v-slot:[`item.delete`]="{ item }">
              <v-icon @click="deleteResult(item)">
                mdi-close
              </v-icon>
            </template>

            <!-- Header -->
            <template v-slot:[`expanded-item`]="{ headers, item }">
              <td :colspan="headers.length">
                <v-row>
                  <!-- dgl cmd -->
                  <v-col cols="6">
                    <v-card>
                      <v-container>
                        <v-textarea
                          v-model="cmd_dgl"
                          label="DGL cmd"
                          readonly
                          height="300px"
                          filled
                        ></v-textarea>
                      </v-container>
                    </v-card>
                  </v-col>

                  <!-- pyg cmd -->
                  <v-col cols="6">
                    <v-card>
                      <v-container>
                        <v-textarea
                          v-model="cmd_pyg"
                          label="PyG cmd"
                          readonly
                          height="300px"
                          filled
                        ></v-textarea>
                      </v-container>
                    </v-card>
                  </v-col>

                </v-row>
              </td>
            </template>

          </v-data-table>
        </v-container>
      </v-card>
    </v-container>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "RecordLisgt",

  components: {},

  data: () => ({
    urls: {
      fetchResultInfos: "/api/queryResultInfos/",
      fetchCmd: "/api/queryCmd/",
      deleteResult: "/api/deleteResult/"
    },
    headers: [
      { text: "Project", value: "project" },
      { text: "Task", value: "task" },
      { text: "Dataset", value: "dataset" },
      { text: "Epoch", value: "epoch" },
      { text: "Minibatch", value: "minibatch" },
      { text: "Layer", value: "layer" },
      { text: "Analyse", value: "analyse", sortable: false },
      { text: "Delete", value: "delete", sortable: false }
    ],
    results: [],
    cmd_dgl: "",
    cmd_pyg: "",
    last_cmd: ""  //用于cmd刷新
  }),

  methods: {
    initial() {
      //this.$store.commit("setIsRoot", false);
      //this.user.uid = this.$store.state.loginUser.uname;
      this.fetchResultInfos();
      this.last_cmd = "";
    },

    //查询所有的Results记录信息
    fetchResultInfos() {
      this.results = [];

      axios({
        method: "post",
        url: this.urls.fetchResultInfos
      })
        .then(async (res) => {
          this.results = [];
          const results = Object.keys(res.data);
          for (let result of results) {
            let tmp = result.split("-");
            this.results.push({project: tmp[0],
                               task: tmp[1],
                               dataset: tmp[2],
                               epoch: tmp[3],
                               minibatch: tmp[4],
                               layer: tmp[5],
                               status: tmp[6],   //1表示训练已完成，否则未完成
                               key: result
            });
          }
        })
        .catch((err) => {
          console.log(err);
        });
    },

    //fetch cmd
    fetchCmd(name) {  //name = project-task-dataset-epoch-minibatch-layer
      this.last_cmd = name; //修改last_cmd
      var params = new URLSearchParams();
      params.append("name", name);
      axios({
        method: "post",
        url: this.urls.fetchCmd,
        data: params,
      })
        .then((res) => {
          this.cmd_dgl = res.data.dgl;
          this.cmd_pyg = res.data.pyg;
          if (res.data.status === '1') {
            console.log("finish");
            this.fetchResultInfos();
            this.last_cmd = "";
          }
        })
        .catch((err) => {
          console.log(err);
        });
    },

    //点击表格的某一行
    onRowClick(item) {
      this.fetchCmd(item.project+'-'+item.task+'-'+item.dataset+'-'+item.epoch+'-'+item.minibatch+'-'+item.layer);
    },

    viewResult(item) {
      this.$store.state.chart_project = item.project+'-'+item.task+'-'+item.dataset+'-'+item.epoch+'-'+item.minibatch+'-'+item.layer;
      this.$router.push("/chart/");
    },

    deleteResult(item) {
      var name = item.project+'-'+item.task+'-'+item.dataset+'-'+item.epoch+'-'+item.minibatch+'-'+item.layer;
      var params = new URLSearchParams();
      params.append("name", name);
      axios({
        method: "post",
        url: this.urls.deleteResult,
        data: params,
      })
        .then((res) => {
          this.initial();
        })
        .catch((err) => {
          console.log(err);
        });
    }
  },

  watch: {
    /*cmd_dgl() {
      setTimeout(() => {
        //实现对cmd的查询
        this.fetchCmd(this.last_cmd);
      }, 1000);
    },

    cmd_pyg() {
      setTimeout(() => {
        //实现对cmd的查询
        this.fetchCmd(this.last_cmd);
      }, 1000);
    },*/
  },

  mounted() {
    this.initial();
    this.timer = setInterval ( () => {
      if (this.last_cmd !== ""){
        console.log("flash");
        this.fetchCmd(this.last_cmd);
      }
    }, 1000)
  },
};
</script>

<style scoped>
@import url("../assets/css/recordlist.css");
@import url("../assets/css/public.css");
</style>

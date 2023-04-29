<template>
  <div class="background-div">
    <v-container>
      <v-card elevation="4" outlined>
        <v-container>
          <v-tabs v-model="tab" grow color="black" background-color="transparent">
            <v-tab v-for="item in items" :key="item">{{ item }}</v-tab>
          </v-tabs>
          <v-tabs-items v-model="tab">
            <v-row>
              <!--total running time-->
              <v-col cols="3">
                <v-card-subtitle>DGL's total running time is <b style="color: brown;">{{ toFixed(dgl_total_time) }}(s)</b></v-card-subtitle>
                <v-card-subtitle>PyG's total running time is <b style="color: brown;">{{ toFixed(pyg_total_time) }}(s)</b></v-card-subtitle>
              </v-col>
              <!--peak memory-->
              <v-col cols="3">
                <v-card-subtitle>DGL's peak memory used is <b style="color: brown;">{{ toFixed(dgl_peak_mem) }}(Mb)</b></v-card-subtitle>
                <v-card-subtitle>PyG's peak memory used is <b style="color: brown;">{{ toFixed(pyg_peak_mem) }}(Mb)</b></v-card-subtitle>
              </v-col>
              <!--ave gpu-->
              <v-col cols="3">
                <v-card-subtitle>DGL's average GPU Utilization is <b style="color: brown;">{{ toFixed(dgl_ave_gpu) }}%</b></v-card-subtitle>
                <v-card-subtitle>PyG's average GPU Utilization is <b style="color: brown;">{{ toFixed(pyg_ave_gpu) }}%</b></v-card-subtitle>
              </v-col>
            </v-row>
            <v-tab-item v-for="item in items" :key="item">
              <!-- Operator View -->
              <v-container v-if="item == 'Operator View'">
                <v-row>
                  <v-col cols="5">
                    <v-slider
                      label="Top Operators To Show"
                      v-model="opNumbersToShow"
                      class="align-center"
                      color="red"
                      :max="numbersToShowMax"
                      :min="numbersToShowMin"
                      hide-details
                    >
                      <template v-slot:append>
                        <v-text-field
                          v-model="opNumbersToShow"
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
                  <v-col cols="6">
                    <v-card outlined hover>
                      <v-card-title>DGL -- Operator Decomposition -- Device (%)</v-card-title>
                      <pie-chart 
                        :data="dglOperatorDevicePie.slice(0, opNumbersToShow)"
                        height="300px"
                      ></pie-chart>
                    </v-card>
                  </v-col>
                  <v-col cols="6">
                    <v-card outlined hover>
                      <v-card-title>PyG -- Operator Decomposition -- Device (%)</v-card-title>
                      <pie-chart
                        :data="pygOperatorDevicePie.slice(0, opNumbersToShow)"
                        height="300px"
                      ></pie-chart>
                    </v-card>
                  </v-col>
                </v-row>               
              </v-container>
              <!-- End Operator View -->

              <!-- Op Compare -->
              <v-container v-else-if="item == 'Operator Compare'">
                <v-card-title>Same Operators Compare</v-card-title>
                <v-row justify-center>
                  <v-col>
                  <line-chart
                    ytitle="Operator Proportion"
                    :data="[
                      { name: 'DGL Proportion', data: dglLinearData },
                      { name: 'PyG Proportion', data: pygLinearData }
                    ]"
                  ></line-chart>
                  </v-col>
                </v-row>
              </v-container>
              <!-- End Op Compare -->

              <!-- GPU Utilization -->
              <v-container v-else>
                <v-row>
                  <v-col cols="6">
                    <v-card outlined hover>
                      <v-card-title>DGL -- GPU Utilization</v-card-title>
                      <line-chart
                      xtitle="time / s"
                      ytitle="GPU Utilization / %"
                      :data="dgl_gpu_utilization"
                    ></line-chart>
                    </v-card>
                  </v-col>
                  <v-col cols="6">
                    <v-card outlined hover>
                      <v-card-title>PyG -- GPU Utilization</v-card-title>
                      <line-chart
                      xtitle="time / s"
                      ytitle="GPU Utilization / %"
                      :data="pyg_gpu_utilization"
                    ></line-chart>
                    </v-card>
                  </v-col>
                </v-row>
              </v-container>
              <!-- End GPU Utilization -->
            </v-tab-item>
          </v-tabs-items>
        </v-container>
      </v-card>
    </v-container>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "Chart",

  components: {},

  data: () => ({
    tab: null,
    items: ["Operator View", "Operator Compare", "GPU Utilization"],
    search: "",
    opNumbersToShow: 8,
    kerNumbersToShow: 8,
    numbersToShowMax: 20,
    numbersToShowMin: 1,

    dgl_total_time: 0.0,
    pyg_total_time: 0.0,

    dgl_ave_gpu: 0.0,
    pyg_ave_gpu: 0.0,

    dgl_peak_mem: 0.0,
    pyg_peak_mem: 0.0,

    pygOperatorDevicePie: [],
    dglOperatorDevicePie: [],
    pygOperatorInfo: [],
    dglOperatorInfo: [],
    
    pygLinearData: {},
    dglLinearData: {},

    dgl_gpu_utilization: {},
    pyg_gpu_utilization: {},

    urls: {
      fetchOperatorInfo: "/api/getOperatorInfo/",
      fetchCostInfo: "/api/queryCost/",
      get_result_url: "/api/getResult/",
    },
  }),

  methods: {
    initial() {
      var chart_project = this.$store.state.chart_project;
      console.log("chart")
      console.log(chart_project)

      var params = new URLSearchParams();
      params.append("name", chart_project);
      axios({
        method: "post",
        url: this.urls.get_result_url,
        data: params,
      })
        .then((res) => {
          console.log(res.data)
          
          this.dgl_total_time = res.data.dgl_total_time
          this.pyg_total_time = res.data.pyg_total_time

          this.dgl_ave_gpu = res.data.dgl_ave_gpu
          this.pyg_ave_gpu = res.data.pyg_ave_gpu

          this.dgl_peak_mem = res.data.dgl_peak_mem
          this.pyg_peak_mem = res.data.pyg_peak_mem          

          this.dglOperatorDevicePie = res.data.dgl_op
          this.pygOperatorDevicePie = res.data.pyg_op
          
          this.dgl_gpu_utilization = res.data.dgl_gpu_persec
          this.pyg_gpu_utilization = res.data.pyg_gpu_persec

          console.log(this.toFixed(this.dgl_total_time))

          this.getLinearData()
        })
        .catch((err) => {
          console.log(err);
        });
        
    },

    getLinearData() {
      var i = 0, j = 0;
      var frac;
      var name;
      for (i = 0; i < this.pygOperatorDevicePie.length; i++) {
        frac = this.pygOperatorDevicePie[i][1];
        name = this.pygOperatorDevicePie[i][0]
        for (j = 0; j < this.dglOperatorDevicePie.length; j++) {
          if (name == this.dglOperatorDevicePie[j][0]) {
            if (
              frac != 0 &&
              this.dglOperatorDevicePie[j][1] != 0
            ) {
              this.pygLinearData[name] = frac;
              this.dglLinearData[name] = this.dglOperatorDevicePie[j][1];
            }
          }
        }
      }
    },

    double2percent(num) {
      return Number(num * 100).toFixed(2) + "%";
    },

    toFixed(num) {
      return Number(num).toFixed(2);
    }
  },

  mounted() {
    this.initial();
  },
};
</script>

<style scoped>
@import url("../assets/css/compare.css");
@import url("../assets/css/public.css");
</style>

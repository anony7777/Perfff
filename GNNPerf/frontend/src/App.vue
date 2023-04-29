<template>
  <v-app>
    <v-app-bar
      v-if="this.$store.state.isRoot != true"
      app
      color="primary"
      src="https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fimg-pre.ivsky.com%2Fimg%2Ftupian%2Fpre%2F201708%2F31%2Fdiannaopingmushangxianshidedaimatupian-014.jpg&refer=http%3A%2F%2Fimg-pre.ivsky.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=jpeg?sec=1648280690&t=8d3f039b59600fb2cd16afe3e4504ae3"
      dark
    >
      <div class="d-flex align-center">
        <a href="/main/">
          <v-img
            alt="Vuetify Logo"
            src="./assets/logo2.svg"
            class="shrink mr-2"
            contain
            transition="scale-transition"
            width="60"
          />
        </a>
        <v-toolbar-title><strong>GNNPerf</strong></v-toolbar-title>
      </div>

      <v-spacer></v-spacer>
      <v-menu left bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon v-bind="attrs" v-on="on">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>

        <v-list>
          <v-list-item
            v-for="item in userListItem"
            :key="item"
            @click="chooseUserListItem(item)"
          >
            <v-list-item-title>{{ item }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>

    <v-footer v-if="this.$store.state.isRoot != true" dark padless>
      <v-card class="flex" flat tile>
        <v-card-title class="blue darken-4">
          <strong class="subheading">One-stop Solution</strong>

          <v-spacer></v-spacer>
        </v-card-title>

        <v-card-text class="py-2 white--text text-center">
          {{ new Date().getFullYear() }} — <strong>GNNPerf</strong>
        </v-card-text>
      </v-card>
    </v-footer>
  </v-app>
</template>

<script>
import "@/assets/js/Global.js";
export default {
  name: "App",

  components: {},

  data: () => ({
    userListItem: ["Projects", "Results"],
  }),

  methods: {
    initial() {
      var pathname = window.location.pathname;
      //this.$store.commit("setIsRoot", true);
    },

    chooseUserListItem(item) {
      if (item == "Projects") {
        this.$router.push({ name: "Main" });
      } else if (item == "Results") {
        this.$router.push({ name: "ResultList" });
      }
    },
  },

  created() {
    this.initial();
  },
};
</script>

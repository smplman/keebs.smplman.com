<template>
  <div id="app">
    <p>This tool is designed to take a JSON keyboard layout from <a href="http://www.keyboard-layout-editor.com/">http://www.keyboard-layout-editor.com/</a> and convert it into an LED config for <a href="https://qmk.fm/">QMK</a></p>
    <h2>Input</h2>
    <p>Choose a JSON file to upload or paste the contents in the input box below</p>
    <FileLoader v-on:file-loaded="fileLoaded"/>
    <form>
      <label>Num Per Line</label>
      <input v-model="options.numPerLine" @change="inputChanged" type="text" name="numPerLine">
      <label>Index Start</label>
      <select v-model="options.indexStart" @change="inputChanged" name="indexStart" id="indexStart">
        <option value="0">0</option>
        <option value="1">1</option>
      </select>
      <label>Index End</label>
      <input v-model="options.indexEnd" @change="inputChanged" type="text" name="indexEnd">
    </form>
    <button @click="inputChanged">Convert</button>
    <textarea v-model="input" @change="inputChanged" @paste="inputPasted"></textarea>
    <h2>Output</h2>
    <textarea v-model="output"></textarea>
  </div>
</template>

<script>
import FileLoader from './components/FileLoader.vue'; 
import { KLEtoRGB }  from './KLEtoRGB.js';

export default {
  name: 'App',
  components: {
    FileLoader
  },
  data: () => {
    return {
      options: {
        indexEnd: 101,
        indexStart: 0,
        numPerLine: 17
      },
      input: '',
      output: ''
    }
  },
  methods: {
    fileLoaded (data) {
      console.log('App loaded file');
      this.parseData(data);
    },
    inputChanged () {
      console.log('Input changed', this.input);
      this.parseData(this.input);
    },
    inputPasted (e) {
      const data = e.clipboardData.getData('text/plain');
      console.log('Input pasted', data);
      this.parseData(data);
    },
    parseData (data) {
      try {
        const jsonData = JSON.parse(data);
        this.input = data;
        this.output = KLEtoRGB(jsonData, this.options);
      } catch (error) {
        console.error(error);
        this.output = error;
      }

    }
  },
  mounted () {
    // this.output = KLEtoRGB({}, this.options);
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

textarea {
  width: 90%;
  height: 30vh;
  margin: 20px 0;
}

label {
  font-weight: bold;
  margin-right: 5px;
}

input, select {
  margin-right: 20px;
}

form {
  margin-top: 20px;
}

button {
  display: block;
  margin: auto;
  margin-top: 20px;
}
</style>

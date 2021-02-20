<template>
  <div>
    <input type="file" ref="myFile" @change="selectedFile">
    <div v-show="error">{{ error }}</div>
    <br/>
  </div>
</template>

<script>
export default {
  name: 'FileLoader',
  data: () => {
  return {
    error: false
    }
  },
  methods:{
    selectedFile () {
      console.log('selected a file');
      console.log(this.$refs.myFile.files[0]);
      
      let file = this.$refs.myFile.files[0];
      if (!file || file.type !== 'application/json') {
        this.error = 'File type must be .json';
        return;
      }
      
      // Credit: https://stackoverflow.com/a/754398/52160
      let reader = new FileReader();
      reader.readAsText(file, "UTF-8");

      reader.onload = () => {
        this.text = reader.result;
        this.$emit('file-loaded', reader.result);
      }

      reader.onerror = (evt) => {
        console.error(evt);
      }
      
    }
  }
}
</script>
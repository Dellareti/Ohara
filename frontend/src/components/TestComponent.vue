<template>
  <div class="test-component">
    <h2>Test Component</h2>
    <p>If you can see this, Vue.js is working!</p>
    <button @click="testClick">Click here</button>
    <p v-if="clicked">Click worked!</p>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'TestComponent',
  setup() {
    const clicked = ref(false)
    
    const testClick = () => {
      clicked.value = true
    }
    
    return {
      clicked,
      testClick
    }
  }
}
</script>

<style scoped>
.test-component {
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  margin: 20px;
  text-align: center;
}

button {
  background: #4ecdc4;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  color: white;
  cursor: pointer;
  margin: 10px;
}

button:hover {
  background: #44a08d;
}
</style>
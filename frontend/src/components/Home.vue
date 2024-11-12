<template>
  <div>
    <h1>Welcome to the Home Page!</h1>
    <p>This is the Home.vue component.</p>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      message: 'This is a message from the Home component.',
    };
  },
  mounted() {
    console.log(this.message);
  },
};
</script>

<style scoped>
/* Add your styles here if needed */
h1 {
  color: blue;
}
</style>

<script setup>
import { RouterView } from 'vue-router';
import Navbar from './components/Navbar.vue';
</script>

<template>
  <header>
  </header>

  <main class="container flex flex-col
              mx-auto px-8 mt-16 mb-16 gap-32
              lg:px-56 lg:gap-48
              xl:px-72 xl:gap-48
              2xl:px-96 2xl:gap-48
              text-lg text-slate-900">
    <Navbar />
    <div class="flex-auto">
      <RouterView />
    </div>
  </main>
</template>

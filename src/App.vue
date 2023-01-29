<script setup>
import { RouterView } from 'vue-router';
import Navbar from './components/Navbar.vue';
</script>

<template>
  <header>
  </header>

  <main class="container flex flex-col
              mx-auto px-8 mt-32 mb-16 gap-8
              lg:px-56 lg:gap-16
              xl:px-72 xl:gap-16
              2xl:px-96 2xl:gap-16
              text-lg text-slate-900">
    <Navbar />
    <div class="flex-auto">
      <RouterView />
    </div>
  </main>
</template>

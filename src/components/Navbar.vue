<script setup>
import { computed, ref, onMounted } from 'vue';
import NavbarItem from './NavbarItem.vue';

let windowWidth = ref(window.innerWidth);

const showFullName = computed(() => {
    return windowWidth.value > 550;
})

onMounted(() => {
    window.addEventListener('resize', () => {
        windowWidth = window.innerWidth;
    })
});

</script>

<template>
    <div class="flex gap-8 items-end
                border-dotted border-b-4 border-sky-900">
        <h1 v-show="showFullName" class="text-slate-800
            text-4xl font-serif font-bold tracking-tighter">
            <span class="text-sky-400 text-xl mr-1">><code class="animate-ping">_</code></span>Jamie Phan
        </h1>
        <h1 v-show="!showFullName" class="text-slate-800
            text-4xl font-serif font-bold tracking-tighter">
            <span class="text-sky-400 text-xl mr-1">><code class="animate-ping">_</code></span>J.P.
        </h1>
        <div class="flex-auto"></div>
        <div class="animate-bounce opacity-0 hover:opacity-100 ease-in-out duration-300">👻<sup
                class="text-red-400 text-xs font-bold"> boo!</sup></div>
        <NavbarItem routeTo="/" label="Home" />
        <NavbarItem routeTo="/" label="About" />
    </div>
</template>
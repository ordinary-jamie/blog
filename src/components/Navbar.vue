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
                border-slate-200" style="border-bottom-width: 1px">
        <h1 v-show="showFullName" class="text-sky-900 text-4xl font-sans tracking-tight font-normal -mb-1">
            <span class="text-sky-500 text-xl font-mono">~$ <span
                class="font-extrabold animate-blink -mr-4">__</span>
            </span>Jamie Phan
        </h1>
        <h1 v-show="!showFullName" class="text-sky-900 text-4xl font-sans tracking-tight font-normal -mb-1">
            <span class="text-sky-500 text-xl font-mono">~$ <span
                class="font-extrabold animate-blink -mr-4">__</span>
            </span>J.P.
        </h1>
        <div class="flex-auto"></div>
        <div class="animate-bounce opacity-0 hover:opacity-100 ease-in-out duration-300">👻<sup
            class="text-red-400 text-xs font-bold"> boo!</sup></div>
        <NavbarItem routeTo="/" label="Home" />
        <NavbarItem routeTo="/about" label="About" />
    </div>
</template>

<style scoped>
.animate-blink {
    animation: blink 1s step-end infinite;
}

@keyframes blink {
    0% {
        opacity: 1.0;
    }

    50% {
        opacity: 0.0;
    }

    100% {
        opacity: 1.0;
    }
}

h1 {
    font-family: "Urbanist";
}
</style>
<script setup>
import { onMounted, onUpdated, ref } from 'vue';
import Prism from "prismjs";
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-bash';
import "prismjs/themes/prism.css";

const props = defineProps({
    assetPath: {
        type: String,
        required: true,
    },
})

const html = ref();

onUpdated(() => {
    Prism.highlightAll();
})

onMounted(async () => {
    const res = await import(`/src/assets/${props.assetPath}.html?raw`);
    html.value = res.default;
});

</script>

<template>
    <div class="text-sm" v-html="html"></div>
</template>

<style lang="postcss" scoped>
:deep(h2) {
    @apply font-bold font-serif text-2xl text-sky-500 mt-16;
}

:deep(h3) {
    @apply font-bold font-serif italic text-xl text-sky-600 mt-8;
}

:deep(p) {
    @apply text-slate-700 my-2 leading-6;
}

:deep(a) {
    @apply text-violet-500 underline hover:animate-pulse;
}

:deep(li) {
    @apply text-slate-700 ml-8;
}

:deep(ul) {
    @apply list-disc;
}

:deep(ol) {
    @apply list-decimal;
}

:deep(table) {
    @apply bg-slate-50 rounded-lg ring-slate-300 ring-1 shadow-md table-auto border-separate border-spacing-1 min-w-full;
}

:deep(th) {
    @apply border border-slate-300 bg-slate-400 px-4 py-1 text-white;
}

:deep(td) {
    @apply border border-slate-200 px-2 py-1;
}

:deep(:not(pre) > code) {
    @apply text-fuchsia-700;
}

:deep(pre, pre>*) {
    @apply bg-slate-100 text-xs;
    text-shadow: none;
}

:deep(pre) {
    @apply p-4 bg-slate-50 rounded-lg ring-slate-300 ring-1 shadow-md select-all;
}

:deep(.token) {
    text-shadow: none;
}

:deep(code) {
    text-shadow: none;
}
</style>
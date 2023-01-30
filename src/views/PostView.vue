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



<style lang="postcss" scoped src="/src/assets/post.css" />
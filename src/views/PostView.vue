<script setup>
import { onMounted, onUpdated, ref } from 'vue';

import Prism from "prismjs";
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-go';
import 'prismjs/components/prism-java';
import 'prismjs/components/prism-http';
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

    const splitName = props.assetPath.split('/');
    if (splitName[0] == "content") {
        if (splitName.length === 3) {
            const res = await import(`@/assets/content/${splitName[1]}/${splitName[2]}.html?raw`);
            html.value = res.default;
        } else {
            const res = await import(`@/assets/content/${splitName[1]}.html?raw`);
            html.value = res.default;
        }
    }
});

</script>

<template>
    <div class="text-sm" v-html="html"></div>
</template>

<style lang="postcss" scoped src="@/assets/post.css">

</style>
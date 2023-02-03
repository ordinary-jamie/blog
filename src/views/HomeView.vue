<script setup>
import { computed, ref } from 'vue';
import PostCard from '../components/PostCard.vue';
import Select from '../components/Select.vue';
import meta from '@/assets/content/meta.json'

const tags = Object.keys(meta.tagRefs);
const sections = Object.keys(meta.sectionRefs);

const tagFilter = ref();
const sectionFilter = ref();


const posts = computed(() => {
    return meta.posts.filter((item) => {
        let ret = true
        if (sectionFilter.value) {
            ret &= item.section == sectionFilter.value;
        }
        if (tagFilter.value) {
            ret &= item.tags.includes(tagFilter.value);
        }
        return ret
    })
})

</script>

<template>
    <div class="flex flex-col gap-2">
        <div class="flex items-end">
            <h1>Posts</h1>
            <div class="flex-grow"></div>
            <Select v-model="tagFilter" label="Tag" prompt="Filter tags" :options="tags" />
            <Select v-model="sectionFilter" label="Section" prompt="Filter section" :options="sections" />
        </div>
        <div class="flex-grow"></div>
        <PostCard v-for="post in posts" :title="post.title" :date="post.date" :section="post.section"
            :routeTo="post.ref" :tags="post.tags">
            {{ post.preview }}
        </PostCard>
    </div>
</template>
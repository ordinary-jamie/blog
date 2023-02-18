<script setup>
import { computed, ref } from 'vue';
import PostCard from '../components/PostCard.vue';
import Select from '../components/Select.vue';
import ButtonX from '../components/ButtonX.vue';
import meta from '@/assets/content/meta.json'

const tags = Object.keys(meta.tagRefs);
const sections = Object.keys(meta.sectionRefs);

const tagFilter = ref();
const sectionFilter = ref();
const showClearButton = ref(true);

const posts = computed(() => {
    return meta.posts.filter((item) => {
        let ret = true
        if (sectionFilter.value) {
            ret &= item.section == sectionFilter.value;
            showClearButton.value = true;
        }
        if (tagFilter.value) {
            ret &= item.tags.includes(tagFilter.value);
            showClearButton.value = true;
        }

        if (!sectionFilter.value && !tagFilter.value) {
            showClearButton.value = false;
        }
        return ret
    })
})

const clearFilters = () => {
    // Clear the filters
    tagFilter.value = null;
    sectionFilter.value = null;

    // Reset select boxes
    const tagSelect = document.getElementById('tagSelect');
    const sectionSelect = document.getElementById('sectionSelect');
    tagSelect.selectedIndex = 0;
    sectionSelect.selectedIndex = 0;
}

</script>

<template>
    <div class="flex flex-col gap-2">
        <div class="flex items-end">
            <h1>Posts</h1>
            <div class="flex-grow"></div>
            <ButtonX v-if="showClearButton" @click="clearFilters"/>
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
<script setup>
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import moment from 'moment';
import PostCardTab from './PostCardTab.vue';

const props = defineProps({
    routeTo: {
        type: String,
        required: true,
    },
    title: {
        type: String,
        required: true,
    },
    date: {
        type: String,
        required: false,
    },
    section: {
        type: String,
        required: true,
    },
    tags: {
        type: Array,
        required: false,
    },
})

const displayDtFields = computed(() => {
    const dt = new Date(Date.parse(props.date));
    const today = new Date(Date.now());
    let yr = dt.getFullYear()
    if (dt.getFullYear() == today.getFullYear()) {
        yr = ""
    }
    return {
        'date': moment(Date.parse(dt)).format("MMM Do"),
        'year': yr,
    }
})

const routeTo = computed(() => {
    return "/posts/" + props.routeTo;
})

</script>

<template>
    <div class="flex flex-col">
        <div class="flex px-2 gap-0" v-if="tags">
            <PostCardTab :label="section" prefix="@" />
            <PostCardTab v-for="tag in tags" :label="tag" />
        </div>
        <RouterLink :to="routeTo">
            <div
                class="p-4 bg-slate-50 rounded-lg ring-slate-300 ring-1 shadow-md hover:ring-sky-500 hover:bg-sky-50 group">
                <div class="flex flex-nowrap">
                    <div>
                        <h1 class="text-slate-700 font-bold">{{ title }}</h1>
                    </div>
                    <div class="grow"></div>
                    <div class="flex flex-col text-right">
                        <span class="text-slate-500 text-sm group-hover:text-sky-600">{{ displayDtFields.date }}</span>
                        <span class="text-slate-500 text-sm group-hover:text-sky-600">{{ displayDtFields.year }}</span>
                    </div>
                </div>
                <div class="flex text-slate-400 font-thin italic text-sm group-hover:text-slate-800">
                    <slot />
                    <div class="w-32 flex-initial"></div>
                </div>
            </div>
        </RouterLink>
    </div>
</template>
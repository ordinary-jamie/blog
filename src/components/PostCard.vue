<script setup>
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import moment from 'moment';

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
        <RouterLink :to="routeTo">
            <div class="p-2 rounded -mx-2 hover:ring-sky-500 hover:bg-sky-50 group">
                <div class="flex flex-nowrap">
                    <div class="flex items-end">
                        <span class="font-mono text-xs sm:text-sm text-slate-500 group-hover:text-sky-500 pb-1">@{{
                            section
                        }}/</span>
                        <h2 class="text-slate-700 font-bold text-sm sm:text-lg">{{ title }}</h2>
                    </div>
                    <div class="grow"></div>
                    <div class="flex flex-col text-right">
                        <span class="w-16 text-slate-500 text-sm group-hover:text-sky-600">{{
                            displayDtFields.date
                        }}</span>
                    </div>
                </div>
                <div class="flex text-slate-400 font-thin text-sm group-hover:text-slate-800 pl-1 items-top">
                    <div>
                        <slot />&thinsp;
                        <template v-for=" (tag, i) in tags">
                            <span class="text-violet-400 group-hover:text-violet-600 text-xs font-mono">#{{
                                tag
                            }}
                            </span>
                            {{ i<tags.length - 1 ? '&thinsp;' : '' }} </template>
                    </div>
                    <div class="w-8 flex-grow"></div>
                    <span class="text-slate-500 text-sm group-hover:text-sky-600">{{
                        displayDtFields.year
                    }}</span>
                </div>
            </div>
        </RouterLink>
    </div>
</template>
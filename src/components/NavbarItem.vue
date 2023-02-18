<script setup>

import { RouterLink } from 'vue-router';

defineProps({
    routeTo: {
        type: String,
        required: true,
    },
    label: {
        type: String,
        required: true,
    }
})

</script>

<template>
    <RouterLink :to="routeTo">
        <div class="group">
            <p class="text-slate-700
                    group-hover:text-sky-500 text-sm font-semibold
                    decoration-slate-700">
                {{ label }}
            </p>
        </div>
    </RouterLink>
</template>
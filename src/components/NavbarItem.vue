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
            <p class="text-sky-900
                    group-hover:text-sky-500 text-sm font-semibold
                    decoration-slate-800">
                {{ label }}
            </p>
        </div>
    </RouterLink>
</template>
<script setup>
const props = defineProps({
    label: {
        type: String,
        required: true,
    },
    prefix: {
        type: String,
        required: false,
        default: "#",
    }
})

const colorMap = {
    "#": {
        'tabText': 'text-emerald-400',
        'border': 'border-emerald-200',
        'prefixText': 'text-emerald-600',
    },
    "@": {
        'tabText': 'text-blue-400',
        'border': 'border-blue-200',
        'prefixText': 'border-blue-900',
    }
}

</script>

<template>
    <div class="font-mono m-0 px-2 h-5 bg-slate-50 hover:bg-sky-100 hover:text-sky-500 hover:border-sky-500 rounded-t-md text-xs border-2 border-b-0 align-bottom self-end"
        :class="[colorMap[props.prefix].tabText, colorMap[props.prefix].border]">
        <span :class="colorMap[props.prefix].prefixText">{{ prefix }}</span>{{ label }}
    </div>
</template>
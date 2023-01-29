<script setup>

defineProps({
    label: {
        type: String,
        required: true,
    },
    prompt: {
        type: String,
        required: false,
    },
    options: {
        type: Array,
        required: true,
    },
    modelValue: String,
});

defineEmits(['update:modelValue'])

</script>

<template>
    <div>
        <select @change="$emit('update:modelValue', $event.target.value)" id="tagSelect"
            class="bg-slate-50 border border-slate-300 text-slate-600 text-xs rounded-lg focus:ring-blue-500 focus:border-blue-500 block py-1 px-2.5">
            <option selected="true" disabled value="">{{ prompt }}</option>
            <option v-for="(opt, idx) in options" :key="idx" :value="opt">{{ opt }}</option>
        </select>
    </div>
</template>
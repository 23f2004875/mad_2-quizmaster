<template>
  <div class="custom-modal-overlay" @click.self="$emit('close')">
    <div class="custom-modal-box">
      <div class="modal-header border-0">
        <slot name="header">
          <h5 class="modal-title">Modal Title</h5>
        </slot>
        <button type="button" class="btn-close btn-close-white" @click="$emit('close')" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <slot />
      </div>
      <div class="modal-footer border-0">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Modal'
}
</script>

<style scoped>
.custom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1050;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.7);

  display: flex;
  align-items: center;
  justify-content: center;
}
.custom-modal-box {
  background-color: #212529;
  color: white;
  padding: 20px;
  border-radius: 6px;
  width: 100%;
  max-width: 450px; 
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
}
</style>

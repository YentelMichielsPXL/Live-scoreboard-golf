<script setup>
</script>

<template>
  <router-view></router-view>
</template>

<!-- LET OP: Geen 'scoped' hier, zodat deze regels voor de HELE app gelden! -->
<style>
/* Zodra het scherm smaller is dan een tablet (GSM modus): */
@media (max-width: 768px) {
  
  #sidebar, 
  .sidebar, 
  aside, 
  .bg-dark.text-white.p-3 { 
    display: none !important; 
  }

  /* Zorg dat de hoofdinhoud (die vaak een marge heeft vanwege de sidebar) 
     nu de volledige 100% breedte van de gsm pakt */
  main, 
  .main-content, 
  .content,
  .col-md-9 {
    margin-left: 0 !important;
    padding-left: 15px !important;
    padding-right: 15px !important;
    width: 100% !important;
    max-width: 100% !important;
  }
}
</style>
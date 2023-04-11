import { createApp } from 'vue';
import 'bootstrap/dist/css/bootstrap.css';


//const app = createApp({
//  data() {
//    return {
//      fromInput: '',
//      toInput: '',
//      fromCities: [],
//      toCities: [],
//      showFromClues: false,
//      showToClues: false
//    }
//  },
//  computed: {
//    filteredFromCities() {
//      return this.fromCities.filter(city => city.startsWith(this.fromInput))
//    },
//    filteredToCities() {
//      return this.toCities.filter(city => city.startsWith(this.toInput))
//    }
//  },
//  methods: {
//    async getFromCities() {
//      try {
//        const response = await fetch(`location/?from=${this.fromInput}`)
//        if (!response.ok) {
//          throw new Error('Failed to fetch cities')
//        }
//        const cities = await response.json()
//        this.fromCities = cities
//        this.showFromClues = true
//      } catch (error) {
//        console.error(error)
//      }
//    },
//    async getToCities() {
//      try {
//        const response = await fetch(`location/?from=${this.fromInput}&to=${this.toInput}&is_end=True`)
//        if (!response.ok) {
//          throw new Error('Failed to fetch cities')
//        }
//        const cities = await response.json()
//        this.toCities = cities
//        this.showToClues = true
//      } catch (error) {
//        console.error(error)
//      }
//    },
//    fillFromInput(clue) {
//      this.fromInput = clue
//      this.showFromClues = false
//    },
//    fillToInput(clue) {
//      this.toInput = clue
//      this.showToClues = false
//    },
//    changeFromBlur() {
//      setTimeout(() => {
//        this.showFromClues = false
//      }, 200);
//    },
//    changeToBlur() {
//      setTimeout(() => {
//        this.showToClues = false
//      }, 200);
//    },
//  }
//});
//
//document.addEventListener('DOMContentLoaded', () => {
//  app.mount('#app');
//});

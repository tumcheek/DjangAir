<template>
  <div class="row g-0 input-group">
    <div class="col-lg-3 position-relative col-md-12">
      <input type="text" class="col-12 p-3" v-model="fromInput" @input="getFromCities" @blur="changeFromBlur" :name="form.start_location.name" :placeholder="form.start_location.label">
      <ul v-if="showFromClues" style="z-index:2;" class="list-group position-absolute col-12">
        <li v-for="(clue, index) in filteredFromCities" :key="index" @click="fillFromInput(clue)" v-text="clue" role="button" class="list-group-item p-3"></li>
      </ul>
    </div>
    <div class="col-lg-3 position-relative col-md-12">
      <input type="text" class="col-12 p-3" v-model="toInput" @input="getToCities" @blur="changeToBlur" :name="form.end_location.name" :placeholder="form.end_location.label">
      <ul v-if="showToClues" style="z-index:2;" class="list-group position-absolute col-12">
        <li v-for="(clue, index) in filteredToCities" :key="index" @click="fillToInput(clue)" v-text="clue" role="button" class="list-group-item p-3"></li>
      </ul>
    </div>
    <div class="col-lg-3 position-relative col-md-12">
      <input :type="inputType" @focus="inputType = 'date'" @blur="inputType = 'text'" class="col-12 p-3" v-model="startDate" :name="form.start_date.name" :placeholder="form.start_date.label">
    </div>
    <div class="col-lg-2 position-relative col-md-12">
      <input type="number" class="col-12 p-3" v-model="passengerNumber" :name="form.passenger_number.name" :placeholder="form.passenger_number.label">
    </div>
    <button type="submit" class="col-lg-1 col-md-12 btn btn-primary">Search</button>
  </div>

</template>
<script>
export default {
  data() {
    return {
      form: {
        start_location: {
          label: "From",
          name: "start_location"
        },
        end_location: {
          label: "To",
          name: "end_location"
        },
        start_date: {
          label: "Start Date",
          name: "start_date"
        },
        passenger_number: {
          label: "Number of Passengers",
          name: "passenger_number"
        },
      },
      fromInput: "",
      toInput: "",
      startDate: "",
      passengerNumber: "",
      fromCities: [],
      toCities: [],
      showFromClues: false,
      showToClues: false,
      inputValue: '',
      inputType: 'text'
    };
  },
  computed: {
    filteredFromCities() {
      return this.fromCities.filter((city) =>
        city.startsWith(this.fromInput)
      );
    },
    filteredToCities() {
      return this.toCities.filter((city) => city.startsWith(this.toInput));
    },
  },
  methods: {
    async getFromCities() {
      try {
        const response = await fetch(`location/?from=${this.fromInput}`);
        if (!response.ok) {
          throw new Error("Failed to fetch cities");
        }
        const cities = await response.json();
        this.fromCities = cities;
        this.showFromClues = true;
      } catch (error) {
        console.error(error);
      }
    },
    async getToCities() {
      try {
        const response = await fetch(
          `location/?from=${this.fromInput}&to=${this.toInput}&is_end=True`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch cities");
        }
        const cities = await response.json();
        this.toCities = cities;
        this.showToClues = true;
      } catch (error) {
        console.error(error);
      }
    },
    fillFromInput(clue) {
      this.fromInput = clue;
      this.showFromClues = false;
    },
    fillToInput(clue) {
      this.toInput = clue;
      this.showToClues = false;
    },
    changeFromBlur() {
      setTimeout(() => {
        this.showFromClues = false;
      }, 200);
    },
    changeToBlur() {
      setTimeout(() => {
        this.showToClues = false;
      }, 200);
    },
  },
};
</script>

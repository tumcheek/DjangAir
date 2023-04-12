<template>
  <form id="app" class="form-inline" @submit.prevent="submitForm">
    <div class="row g-0 input-group">
      <div class="col-lg-3 position-relative col-md-12">
        <input type="text" class="col-12 p-3" v-model="fromInput" @input="getFromCities" @blur="changeFromBlur" :placeholder="form.start_location.label">
        <ul v-if="showFromClues" style="z-index:2;" class="list-group position-absolute col-12">
          <li v-for="(clue, index) in filteredFromCities" :key="index" @click="fillFromInput(clue)" v-text="clue" role="button" class="list-group-item p-3"></li>
        </ul>
      </div>
      <div class="col-lg-3 position-relative col-md-12">
        <input type="text" class="col-12 p-3" v-model="toInput" @input="getToCities" @blur="changeToBlur" :placeholder="form.end_location.label">
        <ul v-if="showToClues" style="z-index:2;" class="list-group position-absolute col-12">
          <li v-for="(clue, index) in filteredToCities" :key="index" @click="fillToInput(clue)" v-text="clue" role="button" class="list-group-item p-3"></li>
        </ul>
      </div>
      <div class="col-lg-3 position-relative col-md-12">
        <input :type="inputType" @focus="inputType = 'date'" @blur="inputType = 'text'" class="col-12 p-3" v-model="startDate" :placeholder="form.start_date.label">
      </div>
      <div class="col-lg-2 position-relative col-md-12">
        <input type="number" class="col-12 p-3" v-model="passengerNumber" :placeholder="form.passenger_number.label">
      </div>
      <button type="submit" class="col-lg-1 col-md-12 btn btn-primary">Search</button>
    </div>
  </form>
</template>
<script>
export default {
  data() {
    return {
      form: {
        start_location: {
          label: "From",
        },
        end_location: {
          label: "To",
        },
        start_date: {
          label: "Start Date",
        },
        passenger_number: {
          label: "Number of Passengers",
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
async submitForm() {
  try {
    const formData = new FormData();
    formData.append("start_location", this.fromInput);
    formData.append("end_location", this.toInput);
    formData.append("start_date", this.startDate);
    formData.append("passenger_number", this.passengerNumber);
    const csrftoken = this.getCookie("csrftoken");
    const response = await fetch("", {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": csrftoken,
      },
    });
    if (!response.ok) {
      throw new Error("Failed to submit form");
    }
    window.location.href = response.url;
  } catch (error) {
    console.error(error);
  }
},
getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
  },
};
</script>

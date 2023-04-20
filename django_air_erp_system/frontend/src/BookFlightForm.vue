<template>
    <div v-for="(n, i) in allPassenger" :id="'passenger-'+ i" class="col-12 row ticket">
        <input class="col-md-12 mb-md-2 mb-lg-0 col-lg-3 mx-lg-3 p-3" placeholder="First name" required name="First name[]"  type="text">
        <input class="col-md-12 mb-md-2 mb-lg-0 col-lg-3 mx-lg-3 p-3" placeholder="Last name" required name="Last name[]"  type="text">
        <input class="col-md-12 mb-md-2 mb-lg-0 col-lg-3 p-3" placeholder="Email" required name="email[]"  type="email">

        <div class="seats col-12">
            <div v-for="(seats, seat_type) in seatsInfo" >
                <h1 class="mt-3">{{seat_type}}</h1>
            <div class="row">
                <div  v-for="(seat,  index) in seats" :key="seat.number"
                    :class="[{ 'selected': selectedSeat[formCount] === seat.number }, { 'unavailable': !seat.is_available }]"
                    class="seat"
                    @click="seatClickHandler(seat, formCount)">
                {{ seat.number }}
                <input type="radio" :id="seat.id" :name="'seat_'+ i" required :value="seat.number" v-model="selectedSeat[i]" hidden>
                </div>
            </div>

            </div>

        </div>

        <div class="options col-12 row mb-4 mt-3">

                <div v-for="option in flight.options" class="option text-center mx-3 col-md-5 col-lg-3 mb-2 border border-primary">
                    <h3 class="option-name">{{ option.name }}</h3>
                    <p class="option-description">{{ option.description }}</p>
                    <p class="option-price">{{ option.price }}</p>
                    <input type="checkbox" :name="'options_' + i"  :value="option.id">
                </div>

        </div>
        <h3 class="fw-light text-center mb-3"> {{ formCount + 1 }}/{{ allPassenger }}</h3>
        <div class="button-container row d-flex justify-content-center">
            <button v-if="formCount > 0" @click="previousPassenger" class="btn btn-lg btn-success col-sm-12 col-lg-3 mt-sm-3 mx-sm-0 mx-lg-3 mt-lg-0" type="button">Previous</button>
            <button v-if="allPassenger > formCount + 1" @click="nextPassenger" class="btn btn-lg btn-success mt-sm-3 col-sm-12 col-lg-3 mt-lg-0" type="button">Next</button>
            <button class="btn btn-lg btn-danger mt-sm-3 mt-lg-0 col-sm-12 mx-sm-0 mx-lg-3 col-lg-3" type="submit">Submit</button>
        </div>




    </div>
    </template>

    <script>
    export default {

        data(){
            return {
                selectedSeat: [null],
                formCount:0,
                allPassenger: parseInt(document.querySelector('#BookFlightForm').getAttribute('data-passengers')),
                slug: document.querySelector('#BookFlightForm').getAttribute('data-slug'),
                date: document.querySelector('#BookFlightForm').getAttribute('data-date'),
                flight: '',
                seatsInfo: ''


            }
        },

        methods:{
        seatClickHandler(seat, form) {

            if (seat.is_available) {
                this.selectedSeat[form] = seat.number;
            }
        },
        nextPassenger() {
            document.getElementById(`passenger-${this.formCount}`).classList.add('d-none');
            this.formCount++;
            document.getElementById(`passenger-${this.formCount}`).classList.remove('d-none');
        },
        previousPassenger() {
            document.getElementById(`passenger-${this.formCount}`).classList.add('d-none');
            this.formCount--;
            document.getElementById(`passenger-${this.formCount}`).classList.remove('d-none');
          }
    },

        mounted() {

            fetch(`/flight/${this.slug}/${this.date}`)
            .then(response => response.json())
            .then(data => {
                this.flight = data.flight
                this.seatsInfo = data.seats
            })
            .catch(error => {
                console.log(error)
            });
            if (this.allPassenger > 1){

            for(let i=1; i < this.allPassenger; i++){

            document.getElementById(`passenger-${i}`).classList.add('d-none');
            }
        }

  }

    }
  </script>

<style scoped>
.seats {
  display: flex;
  flex-direction: column;
  margin-top: 20px;
  margin-bottom: 20px;
}


.seat {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  border-radius: 5px;
  margin-right: 10px;
  margin-bottom: 5px;
  font-size: 18px;
  font-weight: bold;
  background-color: #cfd8dc;
  color: #333;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
}

.seat.unavailable {
  background-color: #e9e9e9;
  color: #b7b7b7;
  cursor: not-allowed;
}

.seat.selected {
  background-color: #007bff;
  color: #fff;
}

@media (max-width: 767.98px) {
  .seat {
    width: 30px;
    height: 30px;
    font-size: 14px;
  }
}
</style>

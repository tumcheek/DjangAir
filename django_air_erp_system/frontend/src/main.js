import { createApp } from 'vue';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap'

import SearchFlightForm from './SearchFlightForm.vue';
import BookFlightForm from './BookFlightForm.vue';

    document.addEventListener('DOMContentLoaded', function() {
createApp(SearchFlightForm).mount('#SearchFlightForm');
});

    document.addEventListener('DOMContentLoaded', function() {
createApp(BookFlightForm).mount('#BookFlightForm');
});

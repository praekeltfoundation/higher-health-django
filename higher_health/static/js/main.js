"use strict";
  let prov = document.getElementById('id_facility_destination_province'),
    uni = document.getElementById('id_facility_destination_university'),
    camp = document.getElementById('id_facility_destination_campus'),
    uniClone = uni.cloneNode(true),
    campClone = camp.cloneNode(true),
    formSubmit = document.getElementById('login_form'),
    addressInput = document.getElementById('autocomplete'),
    latInput = document.getElementById('id_latitude'),
    lngInput = document.getElementById('id_longitude');

  let selected_province = prov.options[prov.selectedIndex];
  if(selected_province.value !== '') {
    showHiddenInputs(selected_province.value, uniClone, uni, universities);
    showHiddenInputs(uni.options[uni.selectedIndex].value, campClone, camp, campuses);
    clearCampus();
    prov.addEventListener('change', function() {
      showHiddenInputs(this.value, uniClone, uni, universities);
      clearCampus();
    });
    uni.addEventListener('change', function() {
      showHiddenInputs(this.value, campClone, camp, campuses);
      camp.parentElement.classList.remove('hidden');
    });
  };
  function showHiddenInputs(elem, clonedElems, selectInputs, csvInputElem) {
    selectInputs.options.length = 0;

    for(let i = 0; i < clonedElems.options.length; i++) {
      let uniChild = clonedElems.options[i];
      if(csvInputElem[uniChild.value] == elem || csvInputElem[uniChild.value] == undefined) {
        selectInputs.appendChild(uniChild);
      }
    }
  };
  function clearCampus() {
    uni.value = '';
    camp.value = '';
    camp.parentElement.classList.add('hidden');
  }


  /* GOOGLE PLACES API: AUTOCOMPLETE */
  let placeSearch, autocomplete;
  const componentForm = {
    street_number: 'short_name',
    route: 'long_name',
    locality: 'long_name',
    country: 'long_name'
  };


  function fillInAddress() {
    // Get the place details from the autocomplete object.
    let cityInput = autocomplete.getPlace();
    for (let component in componentForm) {
      document.getElementById(component).value = '';
    }

    let location = cityInput.geometry.location;
    latInput.value = location.lat();
    lngInput.value = location.lng();

    // Get each component of the address from the place details,
    // and then fill-in the corresponding field on the form.
    for (let i = 0; i < cityInput.address_components.length; i++) {
      let addressType = cityInput.address_components[i].types[0];
      if (componentForm[addressType]) {
        let val = cityInput.address_components[i][componentForm[addressType]];
        document.getElementById(addressType).value = val;
      }
    }
  }
  function initAutocomplete() {
    // Create the autocomplete object, restricting the search predictions to
    // geographical location types.
    autocomplete = new google.maps.places.Autocomplete(
      document.getElementById('autocomplete'), {types: ['geocode']});

    // Avoid paying for data that you don't need by restricting the set of
    // place fields that are returned to just the address components.
    autocomplete.setFields(['address_components', 'geometry']);

    // When the user selects an address from the drop-down, populate the
    // address fields in the form.
    autocomplete.addListener('place_changed', fillInAddress);
  }

  // Bias the autocomplete object to the user's geographical location,
  // as supplied by the browser's 'navigator.geolocation' object.
  function geolocate() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
        let geolocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        let circle = new google.maps.Circle(
          {center: geolocation, radius: position.coords.accuracy});
        autocomplete.setBounds(circle.getBounds());
      });
    }
  }

  /* MEDICAL */
  const checkbox = document.getElementById('healthcheck_terms'),
  questionnairesForm = document.getElementById('questionnaires'),
  addressField = document.getElementById('autocomplete'),
  preexistingconditionsYes= document.getElementById('id_history_pre_existing_condition_0'),
  preexistingconditionsNo= document.getElementById('id_history_pre_existing_condition_1'),
  preexistingconditionsNotsure= document.getElementById('id_history_pre_existing_condition_2');
  document.addEventListener('DOMContentLoaded',function(e) {
    //Review & cleanup
    let checkboxKey = sessionStorage.getItem('checkbox');
    if(checkboxKey === 'true') {
      checkbox.checked = true;
      questionnairesForm.classList.add('showing');
      questionnairesForm.classList.remove('hidden');
    } else {
      checkbox.checked = false;
      questionnairesForm.classList.add('hidden');
      questionnairesForm.classList.remove('showing');
    }
    checkbox.addEventListener('change', function(e){
      if (e.target.checked) {
        sessionStorage.setItem('checkbox', 'true');
        questionnairesForm.classList.add('showing');
        questionnairesForm.classList.remove('hidden');
      } else {
        sessionStorage.setItem('checkbox', 'false');
        questionnairesForm.classList.add('hidden');
        questionnairesForm.classList.remove('showing');
      }
    });

    //Pre-existing conditions Yes & cleanup
    let preexistingRadioKey = sessionStorage.getItem('preexistingRadio');
    if(preexistingRadioKey === 'true' || preexistingRadioKey === 'not_sure') {
      preexistingconditionsYes.checked = true;
      preexistingconditionsForm.classList.add('showing');
      preexistingconditionsForm.classList.remove('hidden');
    } else {
      preexistingconditionsYes.checked = false;
      preexistingconditionsForm.classList.add('hidden');
      preexistingconditionsForm.classList.remove('showing');
    }
    preexistingconditionsYes.addEventListener('change', function(e){
      if (e.target.checked) {
        sessionStorage.setItem('preexistingRadio', 'true');
        preexistingconditionsForm.classList.add('showing');
        preexistingconditionsForm.classList.remove('hidden');
      } else {
        sessionStorage.setItem('preexistingRadio', 'false');
        preexistingconditionsForm.classList.add('hidden');
        preexistingconditionsForm.classList.remove('showing');
      }
    });

    preexistingconditionsNo.addEventListener('change', function(e){
      if (e.target.checked) {
        sessionStorage.setItem('preexistingRadio', 'false');
        preexistingconditionsForm.classList.add('hidden');
        preexistingconditionsForm.classList.remove('showing');
      }
    });
    preexistingconditionsNotsure.addEventListener('change', function(e){
      if (e.target.checked) {
        sessionStorage.setItem('preexistingRadio', 'true');
        preexistingconditionsForm.classList.add('showing');
        preexistingconditionsForm.classList.remove('hidden');
      } else {
        sessionStorage.setItem('preexistingRadio', 'false');
        preexistingconditionsForm.classList.add('hidden');
        preexistingconditionsForm.classList.remove('showing');
      }
    });
    latInput.value = sessionStorage.getItem('lat');
    lngInput.value = sessionStorage.getItem('lng');
    formSubmit.addEventListener('submit',function(e) {
      if(latInput.value !== '' || lngInput.value !== '') {
        sessionStorage.setItem('lat',latInput.value);
        sessionStorage.setItem('lng',lngInput.value);
      }
    });
  });

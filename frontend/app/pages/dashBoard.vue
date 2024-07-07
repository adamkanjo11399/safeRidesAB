<script lang="ts" setup>
import { ref } from 'vue'

import io from 'socket.io-client';

definePageMeta({ layout: 'page' })
useHead({ title: 'Driver dashBoard' })

const zoom = ref(11)
const markers = ref([
  {
    name: 'Station name',
    location: [57.829657, 11.996441]
  }
])


// const image = ref({
//   url: 'https://www.newsobserver.com/news/traffic/ml4bo0/picture176087666/alternates/FREE_1140/STUCK',
//   danger: false,
// })

const image = ref<string | null>(null);

// const path    = ref(markers.value.map((x) => x.location))
const counter = ref(0)
const goal    = ref(markers.value.length)

// const from_marker = ref<Float32Array>(markers.value[counter.value].location)
// const to_marker   = ref<Float32Array>(markers.value[counter.value + 1].location)

const circle    = ref([57.829657, 11.996441])
const driver = ref([57.726417, 11.980239])
const radius    = 3000
const home_view = ref(driver.value)
const show_image_state         = ref<boolean>(false)
const show_driver_state        = ref(true)

async function makeGetRequest(url: string): Promise<any> {
    try {
        const response = await fetch(url);

        // Check if the request was successful (status code 2xx)
        if (!response.ok) {
            throw new Error(`Request failed with status: ${response.status}`);
        }

        // Parse and return the JSON response
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`Error making GET request: ${error.message}`);
        throw error;
    }
}

async function makePostRequest(url: string, data: any): Promise<any> {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // You may need to add additional headers here based on your API requirements
            },
            body: JSON.stringify(data),
        });

        // Check if the request was successful (status code 2xx)
        if (!response.ok) {
            throw new Error(`Request failed with status: ${response.status}`);
        }

        // Parse and return the JSON response
        const responseData = await response.json();
        return responseData;
    } catch (error) {
        console.error(`Error making POST request: ${error.message}`);
        throw error;
    }
}

// Function to get current location
async function getCurrentLocation() {
  if ('geolocation' in navigator) {
    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
      });

      // Update driver's position
      driver.value = [position.coords.latitude, position.coords.longitude];
      home_view.value = driver.value; // Optionally center the map on the new location
    } catch (error) {
      console.error('Error getting location:', error);
      // Handle error (e.g., user denied permission, position unavailable)
    }
  } else {
    console.error('Geolocation is not supported by this browser.');
    // Handle lack of support for geolocation
  }
}

// Socket.io setup
const socket = io('http://192.168.240.163:9094'); // Replace with your server IP and port

// Function to connect to socket.io server
async function connectToSocket(token: string) {
  try {
    await socket.connect();
    socket.emit('join_room', { room: 'zone_1', token }); // Replace with your room and token logic

    const data = {
      "activate_camera": true
    }
    
    socket.emit('send_message', { room: 'zone_1', 'message': data }); // Replace with your room and token logic

    // Handle socket events
    socket.on('message', (data) => {
      // console.log('Received message:', message);
      // Handle received message
      image.value = `data:image/jpeg;base64, ${data.image}`;
      show_image_state.value = true; // Show image when received
      
    });
    
    console.log('Connected to server');

    socket.on('disconnect', () => {
      console.log('Disconnected from server');
      // Handle disconnection
    });
    
  } catch (error) {
    console.error('Error connecting to socket server:', error);
    // Handle connection error
  }
}

// Fetch current location when component is mounted
onMounted(() => {
  connectToSocket('valid_token_1');
  getCurrentLocation();
});

</script>

<template>
  <LayoutPageWrapper>
    <LayoutPageHeader>
      <LayoutPageTitle text="" class="capitalize" />
    </LayoutPageHeader>
    <!-- {{ path }} -->
    <LayoutPageSection>
      <LayoutPageSectionTitle text="" />

      <div class="grid grid-cols-2 gap-5">
        <div>
          <div style="height: 800px; width: 100%">
            <LMap ref="map" :zoom="zoom" :center="home_view">
              <LTileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&amp;copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
                layer-type="base"
                name="OpenStreetMap"
              />

              <div v-for="marker in markers">
                <l-marker :lat-lng="marker.location">
                  <l-popup> Station name </l-popup>
                </l-marker>
              </div>

              <l-circle
                :lat-lng="circle"
                color="red"
                :radius="radius"
              ></l-circle>

              <!-- <l-polyline :lat-lngs="path" color="black" opacity="1">
              </l-polyline> -->

              <l-marker v-if="show_driver_state" :lat-lng="driver">
                <l-icon
                  icon-url="https://icons.iconarchive.com/icons/google/noto-emoji-travel-places/512/42533-train-icon.png"
                  :icon-size="[50, 50]"
                />
              </l-marker>
            </LMap>
          </div>
        </div>
        <div>
          <div>
            <h2 class="text-4xl font-bold dark:text-white">
              General information
            </h2>
            <br />

            <div class="grid grid-cols-2">
              <div>
                <p class="text-lg font-bold dark:text-white">Driver name</p>
                <p class="text-lg font-bold dark:text-white">Driver ID</p>
                <p class="text-lg font-bold dark:text-white">Next station</p>
              </div>
              <div>
                <p>: xxxxx</p>
                <p>: xxxxx</p>
                <p>: xxxxx</p>
              </div>
            </div>

            <!-- <div class="grid grid-cols-3">
              <div>
                <br />
                <button
                  type="button"
                  class="focus:outline-none text-white bg-green-700 hover:bg-green-800 focus:ring-4 focus:ring-green-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800"
                  @click="startSimulation"
                >
                  Start driving
                </button>
              </div>

              <div>
                <br />
                <button
                  type="button"
                  class="focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900"
                  @click="stopSimulation"
                >
                  Full brake
                </button>
              </div>

              <div>
                <br />
                <button
                  type="button"
                  class="focus:outline-none text-white bg-green-700 hover:bg-green-800 focus:ring-4 focus:ring-green-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800"
                  @click="continueSimulation"
                >
                  Continue driving
                </button>
              </div>
            </div>
             -->
          </div>

          <LayoutPageSectionTitle
            v-if="show_image_state"
            text="Taken 10 seconds ago"
          />

          <div>
            <figure v-if="show_image_state" class="max-w-lg">
              <img
                class="h-auto max-w-full rounded-lg"
                :src="image"
                alt="image description"
              />
              <!-- <figcaption class="mt-2 text-sm text-center text-gray-500 dark:text-gray-400">Taken 45 seconds ago</figcaption> -->
            </figure>
          </div>
        </div>
      </div>
    </LayoutPageSection>
  </LayoutPageWrapper>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import io from 'socket.io-client';

definePageMeta({ layout: 'page' })
useHead({ title: 'Driver dashBoard' })

const zoom = ref(11)
const markers = ref([
  {
    name: 'Station name',
    location: [57.794721, 11.885430]
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
let room_joined:boolean = false;

// const from_marker = ref<Float32Array>(markers.value[counter.value].location)
// const to_marker   = ref<Float32Array>(markers.value[counter.value + 1].location)

// const circle    = ref([57.794721, 11.885430])
const circle    = ref([57.726417, 11.980239])
const driver = ref([57.688064, 11.9865344])


function swapValues() {
  if (circle.value[0] == 57.688064) {
    console.log(1)
    circle.value = [57.794721, 11.885430];
  } else {
    console.log(2)
    circle.value = [57.688064, 11.9865344];
  }
    
  console.log('swapValues', circle.value);
  
  setTimeout(swapValues, 20000); // 10000 milliseconds = 10 seconds
}

const radius    = 5000
const home_view = ref(driver.value)
const show_image_state         = ref<boolean>(false)
const show_driver_state        = ref(true)
const socket = io('http://192.168.10.213:9094'); // Replace with your server IP and port

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

function haversineDistance(coords1: number[], coords2: number[]): number {
  const toRad = (x: number) => (x * Math.PI) / 180;

  const lat1 = coords1[0];
  const lon1 = coords1[1];
  const lat2 = coords2[0];
  const lon2 = coords2[1];

  const R = 6371e3; // Radius of the Earth in meters
  const φ1 = toRad(lat1);
  const φ2 = toRad(lat2);
  const Δφ = toRad(lat2 - lat1);
  const Δλ = toRad(lon2 - lon1);

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  const distance = R * c;
  return distance;
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

      const distance = haversineDistance(driver.value, circle.value);
      console.log("distance", distance)
      if (distance <= radius) {
        if (!room_joined) {
          await join_room()
          await activateCamera();
        }
      } else {
        await deactivateCamera();
        await disconnectFromSocket();
      }
    } catch (error) {
      console.error('Error getting location:', error);
    }
  } else {
    console.error('Geolocation is not supported by this browser.');
  }
}

async function join_room() {
  try {
    await socket.connect();
    socket.emit('join_room', { room: 'zone_1', id: 'train_1' });
    console.log('Joining room...');
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for 1 second
    if (!socket.connected) {
      throw new Error('Socket connection failed');
    }
    room_joined = true;
    console.log('Room joined successfully!');
  } catch (error) {
    console.error('Error while joining room:', error);
    // Retry after 1 second
    await new Promise(resolve => setTimeout(resolve, 1000));
    await join_room(); // Recursive call to retry joining
  }
}


// Function to connect to socket.io server
async function activateCamera() {
  console.log('activateCamera')
  try {
     
    const data = {
      "activate_camera": true
    }
    
    socket.emit('send_message', { room: 'zone_1', 'message': data }); 

    // Handle socket events
    socket.on('message', (data) => {
      // console.log('Received message:', message);
      // Handle received message
      image.value = `data:image/jpeg;base64, ${data.image}`;
      show_image_state.value = true; // Show image when received
      
    });
    
    socket.on('disconnect', () => {
      console.log('Disconnected from server');
      show_image_state.value = false;
      room_joined = false;
    });
    
  } catch (error) {
    console.error('Error connecting to socket server:', error);
    // Handle connection error
  }
}

async function deactivateCamera() {
  if (socket.connected) {
    const data = {
      "activate_camera": false
    }
    await socket.emit('send_message', { room: 'zone_1', 'message': data });
    socket.disconnect();
    show_image_state.value = false;
    room_joined = false;
  }
}

async function disconnectFromSocket() {
  if (socket.connected) {
    await socket.disconnect();
    show_image_state.value = false;
    room_joined = false;
  }
}

onMounted(() => {
  setInterval(getCurrentLocation, 5000);
  swapValues();
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
              </div>
              <div>
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

          <!-- <br> -->
          
          <!-- <h2 class="text-4xl font-bold dark:text-white">
              Live stream
          </h2> -->

          <br>
          <div>
            <figure v-if="show_image_state" class="max-w-lg">
              
              <div role="alert">
                <div class="bg-red-500 text-white font-bold rounded-t px-4 py-2">
                  Danger railway crossing
                </div>
                <div class="border border-t-0 border-red-400 rounded-b bg-red-100 px-4 py-3 text-red-700">
                  <p>Be careful</p>
                </div>
              </div> 
              
               <br> 
              
              <!-- <div class="bg-teal-100 border-t-4 border-teal-500 rounded-b text-teal-900 px-4 py-3 shadow-md" role="alert">
                <div class="flex">
                  <div class="py-1"><svg class="fill-current h-6 w-6 text-teal-500 mr-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zm12.73-1.41A8 8 0 1 0 4.34 4.34a8 8 0 0 0 11.32 11.32zM9 11V9h2v6H9v-4zm0-6h2v2H9V5z"/></svg></div>
                  <div>
                    <p class="font-bold">Safe railway crossing</p>
                    <p class="text-sm">Make sure you double check.</p>
                  </div>
                </div>
              </div>
              
              <br> -->

              <img
                class="h-auto max-w-full rounded-lg"
                :src="image"
                alt="image description"
              />
              </figure>
          </div>
          
        </div>
      </div>
    </LayoutPageSection>
  </LayoutPageWrapper>
</template>
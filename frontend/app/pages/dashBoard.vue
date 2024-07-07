<script lang="ts" setup>
import { ref } from 'vue'
import Test from './test.vue';
definePageMeta({ layout: 'page' })
useHead({ title: 'Driver dashBoard' })

const zoom = ref(3)
const markers = ref([
  {
    name: 'Station name',
    location: [57.726417, 11.980239]
  },
  {
    name: 'Station name',
    location: [57.829657, 11.996441]
  }
])

const image = ref({
  url: 'https://www.newsobserver.com/news/traffic/ml4bo0/picture176087666/alternates/FREE_1140/STUCK',
  danger: false,
})

const path    = ref(markers.value.map((x) => x.location))
const counter = ref(0)
const goal    = ref(markers.value.length)

const from_marker = ref<Float32Array>(markers.value[counter.value].location)
const to_marker   = ref<Float32Array>(markers.value[counter.value + 1].location)

const circle    = ref<Float32Array>(to_marker.value)
const radius    = 3000
const home_view = ref<Float32Array>(from_marker.value)

const driver = ref<Float32Array>(from_marker.value)
const k = ref(
  (from_marker.value[1] - to_marker.value[1]) /
  (from_marker.value[0] - to_marker.value[0]),
)

const dt                       = ref(0.0005)
const m                        = ref(from_marker.value[1] - k.value * from_marker.value[0])
const distance_between_markers = ref(haversineDistance(from_marker.value, to_marker.value))
const driver_leftover_distance = ref()
const driver_driven_distance   = ref()
const show_image_state         = ref<boolean>(false)
const show_driver_state        = ref(false)

const simulation_state = ref<boolean>(false)
const step             = ref(from_marker.value[0])

function haversineDistance(coord1: Float32Array, coord2: Float32Array) {
  const [lat1, lon1] = coord1
  const [lat2, lon2] = coord2

  const R = 6371000

  const dLat = (lat2 - lat1) * (Math.PI / 180)
  const dLon = (lon2 - lon1) * (Math.PI / 180)

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) *
      Math.cos(lat2 * (Math.PI / 180)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2)

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

  const distance = R * c

  return distance
}

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function startSimulation() {
  show_driver_state.value = true

  for (let index = 0; index < 9; index++) {
    zoom.value += 1
    await sleep(200)
  }

  simulation_state.value = true
  await sleep(2000)

  const timerId = setInterval(async () => {
    if (simulation_state.value) {
      step.value += dt.value
      const newY = step.value * k.value + m.value

      driver.value = [step.value, newY]

      home_view.value = driver.value

      driver_leftover_distance.value = haversineDistance(
        driver.value,
        to_marker.value,
      )
      driver_driven_distance.value = haversineDistance(
        driver.value,
        from_marker.value,
      )

      // ON THE STOP STATION
      if (driver_driven_distance.value >= distance_between_markers.value) {
        counter.value += 1
        from_marker.value = markers.value[counter.value].location
        to_marker.value = markers.value[counter.value + 1].location
        k.value =
          (from_marker.value[1] - to_marker.value[1]) /
          (from_marker.value[0] - to_marker.value[0])
        m.value = from_marker.value[1] - k.value * from_marker.value[0]
        distance_between_markers.value = haversineDistance(
          from_marker.value,
          to_marker.value,
        )

        circle.value = to_marker.value

        if (counter.value == 1) {
          show_image_state.value = false
          image.value.url =
            'https://www.frantzlawgroup.com/wp-content/uploads/2023/01/railroad.webp'
          image.value.danger = false
        }

        if (counter.value == 2) {
          show_image_state.value = false
          image.value.url =
            'https://jocoreport.com/wp-content/uploads/2023/02/Preston-Street-Rail-Crossing-Selma-02-21-23-2M-scaled.jpg'
          image.value.danger = false
        }
      }

      // BEFORE THE STOP STATION
      if (driver_leftover_distance.value <= radius) {
        if (counter.value == 0) {
          image.value.danger = true
        }

        if (counter.value == 1) {
          image.value.danger = true
        }

        if (counter.value == 2) {
          image.value.danger = false
        }

        // Inside the circle -> show the images taken from the camera
        dt.value = 0.0001
        show_image_state.value = true
      } else {
        dt.value = 0.0005
        show_image_state.value = false
      }

      if (counter.value == goal.value - 1) {
        clearInterval(timerId)
      }
    }
  }, 50)
}

function stopSimulation() {
  simulation_state.value = false
}

function continueSimulation() {
  zoom.value = 12
  simulation_state.value = true
}

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

            <div class="grid grid-cols-3">
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
          </div>

          <LayoutPageSectionTitle
            v-if="show_image_state"
            text="Taken 10 seconds ago"
          />

          <div>
            <figure v-if="show_image_state" class="max-w-lg">
              <img
                class="h-auto max-w-full rounded-lg"
                :src="image.url"
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

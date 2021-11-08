// List of Home-Assistant configuration for MQTT Discovery
// https://www.home-assistant.io/docs/mqtt/discovery/

module.exports = {
  
  sensor_gazpar_gas: {
    type: 'sensor',
    object_id: 'gazpar_gas',
    discovery_payload: {
      device_class: 'gas'
      name: 'gazpar_gas'
      state_topic: '<discovery_prefix>/sensor/gazpar/state
      unit_of_measurement: 'm3'
      value_template: '{{ value_json.value }}',
    }
  },
  sensor_gazpar_energy: {
    type: 'sensor',
    object_id: 'gazpar_energy',
    discovery_payload: {
      device_class: 'energy'
      name: 'gazpar_energy'
      state_topic: '<discovery_prefix>/sensor/gazpar/state
      unit_of_measurement: 'kWh'
      value_template: '{{ value_json.value }}',
    }
  }
}

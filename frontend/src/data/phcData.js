export const phcData = [
  {
    id: "phc-1",
    name: "Central District Hospital",
    block: "North Block",
    lat: 12.9716,
    lng: 77.5946,
    stockItems: [
      { itemName: "Paracetamol 500mg", currentUnits: 5000, avgDailyConsumption: 100 },
      { itemName: "Amoxicillin 250mg", currentUnits: 1000, avgDailyConsumption: 20 },
      { itemName: "ORS Packets", currentUnits: 200, avgDailyConsumption: 100 } // Warning (48 hrs)
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-2",
    name: "Green Valley PHC",
    block: "North Block",
    lat: 12.9816,
    lng: 77.5846,
    stockItems: [
      { itemName: "Paracetamol 500mg", currentUnits: 200, avgDailyConsumption: 150 }, // Critical (<48 hrs)
      { itemName: "IV Fluids", currentUnits: 800, avgDailyConsumption: 50 },
      { itemName: "Syringes", currentUnits: 10000, avgDailyConsumption: 500 }
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-3",
    name: "Lakeview Clinic",
    block: "South Block",
    lat: 12.9116,
    lng: 77.6046,
    stockItems: [
      { itemName: "Amoxicillin 250mg", currentUnits: 150, avgDailyConsumption: 100 }, // Critical
      { itemName: "Bandages", currentUnits: 300, avgDailyConsumption: 100 }, // Warning
      { itemName: "ORS Packets", currentUnits: 5000, avgDailyConsumption: 50 } // Surplus
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-4",
    name: "Hilltop Health Center",
    block: "East Block",
    lat: 12.9516,
    lng: 77.6546,
    stockItems: [
      { itemName: "Paracetamol 500mg", currentUnits: 8000, avgDailyConsumption: 120 }, // Surplus
      { itemName: "Amoxicillin 250mg", currentUnits: 2500, avgDailyConsumption: 30 },
      { itemName: "IV Fluids", currentUnits: 100, avgDailyConsumption: 60 } // Critical
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-5",
    name: "Riverside Medical",
    block: "West Block",
    lat: 12.9616,
    lng: 77.5246,
    stockItems: [
      { itemName: "Paracetamol 500mg", currentUnits: 600, avgDailyConsumption: 250 }, // Critical
      { itemName: "Syringes", currentUnits: 4000, avgDailyConsumption: 200 },
      { itemName: "Bandages", currentUnits: 50, avgDailyConsumption: 10 } // Healthy
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-6",
    name: "Sunrise Care",
    block: "North Block",
    lat: 12.9916,
    lng: 77.5746,
    stockItems: [
      { itemName: "ORS Packets", currentUnits: 80, avgDailyConsumption: 50 }, // Critical
      { itemName: "IV Fluids", currentUnits: 500, avgDailyConsumption: 40 },
      { itemName: "Syringes", currentUnits: 1200, avgDailyConsumption: 150 } // Healthy
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-7",
    name: "Pine Grove Clinic",
    block: "South Block",
    lat: 12.9216,
    lng: 77.5846,
    stockItems: [
      { itemName: "Paracetamol 500mg", currentUnits: 3000, avgDailyConsumption: 80 },
      { itemName: "Amoxicillin 250mg", currentUnits: 1200, avgDailyConsumption: 25 },
      { itemName: "Bandages", currentUnits: 800, avgDailyConsumption: 40 }
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-8",
    name: "Maple Leaf Medical",
    block: "East Block",
    lat: 12.9616,
    lng: 77.6646,
    stockItems: [
      { itemName: "IV Fluids", currentUnits: 200, avgDailyConsumption: 90 }, // Critical
      { itemName: "Syringes", currentUnits: 5000, avgDailyConsumption: 200 },
      { itemName: "ORS Packets", currentUnits: 1500, avgDailyConsumption: 50 }
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-9",
    name: "Oaktree Health",
    block: "West Block",
    lat: 12.9416,
    lng: 77.5146,
    stockItems: [
      { itemName: "Amoxicillin 250mg", currentUnits: 400, avgDailyConsumption: 150 }, // Warning
      { itemName: "Bandages", currentUnits: 600, avgDailyConsumption: 200 }, // Warning
      { itemName: "Paracetamol 500mg", currentUnits: 4500, avgDailyConsumption: 100 } // Healthy
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-10",
    name: "Willow Branch Clinic",
    block: "North Block",
    lat: 12.9856,
    lng: 77.5996,
    stockItems: [
      { itemName: "Syringes", currentUnits: 300, avgDailyConsumption: 200 }, // Critical
      { itemName: "ORS Packets", currentUnits: 3000, avgDailyConsumption: 100 }, // Surplus
      { itemName: "IV Fluids", currentUnits: 800, avgDailyConsumption: 40 }
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-11",
    name: "Cedar Point Center",
    block: "South Block",
    lat: 12.9156,
    lng: 77.5956,
    stockItems: [
      { itemName: "Paracetamol 500mg", currentUnits: 2500, avgDailyConsumption: 100 },
      { itemName: "Amoxicillin 250mg", currentUnits: 100, avgDailyConsumption: 60 }, // Critical
      { itemName: "Bandages", currentUnits: 400, avgDailyConsumption: 50 }
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-12",
    name: "Birchwood Health",
    block: "East Block",
    lat: 12.9556,
    lng: 77.6756,
    stockItems: [
      { itemName: "IV Fluids", currentUnits: 1000, avgDailyConsumption: 60 },
      { itemName: "Syringes", currentUnits: 8000, avgDailyConsumption: 300 }, // Surplus
      { itemName: "ORS Packets", currentUnits: 400, avgDailyConsumption: 250 } // Critical
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-13",
    name: "Elm Street Clinic",
    block: "West Block",
    lat: 12.9356,
    lng: 77.5056,
    stockItems: [
      { itemName: "Paracetamol 500mg", currentUnits: 120, avgDailyConsumption: 100 }, // Critical
      { itemName: "Bandages", currentUnits: 1000, avgDailyConsumption: 80 },
      { itemName: "Amoxicillin 250mg", currentUnits: 800, avgDailyConsumption: 40 }
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-14",
    name: "Ash Grove Medical",
    block: "North Block",
    lat: 12.9956,
    lng: 77.5856,
    stockItems: [
      { itemName: "Syringes", currentUnits: 2000, avgDailyConsumption: 150 },
      { itemName: "ORS Packets", currentUnits: 600, avgDailyConsumption: 80 },
      { itemName: "IV Fluids", currentUnits: 150, avgDailyConsumption: 80 } // Critical
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-15",
    name: "Chestnut Care",
    block: "South Block",
    lat: 12.9056,
    lng: 77.6156,
    stockItems: [
      { itemName: "Paracetamol 500mg", currentUnits: 5000, avgDailyConsumption: 150 },
      { itemName: "Amoxicillin 250mg", currentUnits: 2000, avgDailyConsumption: 60 },
      { itemName: "Bandages", currentUnits: 150, avgDailyConsumption: 60 } // Warning
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-16",
    name: "Walnut Ridge Clinic",
    block: "East Block",
    lat: 12.9456,
    lng: 77.6856,
    stockItems: [
      { itemName: "IV Fluids", currentUnits: 400, avgDailyConsumption: 50 },
      { itemName: "Syringes", currentUnits: 150, avgDailyConsumption: 100 }, // Critical
      { itemName: "ORS Packets", currentUnits: 2000, avgDailyConsumption: 100 }
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-17",
    name: "Spruce Hollow Health",
    block: "West Block",
    lat: 12.9256,
    lng: 77.5156,
    stockItems: [
      { itemName: "Paracetamol 500mg", currentUnits: 300, avgDailyConsumption: 120 }, // Warning
      { itemName: "Bandages", currentUnits: 500, avgDailyConsumption: 100 }, // Healthy
      { itemName: "Amoxicillin 250mg", currentUnits: 500, avgDailyConsumption: 50 } // Healthy
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-18",
    name: "Sycamore Medical",
    block: "North Block",
    lat: 12.9756,
    lng: 77.5656,
    stockItems: [
      { itemName: "Syringes", currentUnits: 6000, avgDailyConsumption: 250 },
      { itemName: "ORS Packets", currentUnits: 100, avgDailyConsumption: 80 }, // Critical
      { itemName: "IV Fluids", currentUnits: 600, avgDailyConsumption: 60 }
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-19",
    name: "Magnolia Health",
    block: "South Block",
    lat: 12.9356,
    lng: 77.6256,
    stockItems: [
      { itemName: "Paracetamol 500mg", currentUnits: 4000, avgDailyConsumption: 100 },
      { itemName: "Amoxicillin 250mg", currentUnits: 250, avgDailyConsumption: 100 }, // Warning
      { itemName: "Bandages", currentUnits: 1200, avgDailyConsumption: 80 }
    ],
    lastUpdated: new Date().toISOString()
  },
  {
    id: "phc-20",
    name: "Dogwood Clinic",
    block: "East Block",
    lat: 12.9356,
    lng: 77.6556,
    stockItems: [
      { itemName: "IV Fluids", currentUnits: 1500, avgDailyConsumption: 80 },
      { itemName: "Syringes", currentUnits: 4000, avgDailyConsumption: 200 },
      { itemName: "ORS Packets", currentUnits: 3000, avgDailyConsumption: 150 }
    ],
    lastUpdated: new Date().toISOString()
  }
];

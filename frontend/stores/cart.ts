import { createSlice } from "@reduxjs/toolkit";

interface itemState {
  patient_id: number;
  data: { description: string; uid: string }[];
}

interface cartState {
  items: itemState[];
}

const initialState: cartState = {
  items: []
};

const cartSlice = createSlice({
  name: "cart",
  initialState,
  reducers: {
    setCart(state, action) {
      state.items = action.payload;
    },
    addToCart(state, action) {
      const { patient_id, description, uid } = action.payload;
      const patientIndex = state.items.findIndex(
        (item) => item.patient_id === patient_id
      );
      if (patientIndex <= -1) {
        state.items.push({
          patient_id: patient_id,
          data: [{ description: description, uid: uid }]
        });
      } else {
        const itemIndex = state.items[patientIndex].data.findIndex(
          (_data) => _data.uid === uid
        );
        if (itemIndex <= -1) {
          state.items[patientIndex].data.push({
            description: description,
            uid: uid
          });
        }
      }
    },
    removeFromCart(state, action) {
      const { patient_id, uid } = action.payload;

      const patientIndex = state.items.findIndex(
        (item) => item.patient_id === patient_id
      );
      if (patientIndex > -1) {
        const itemIndex = state.items[patientIndex].data.findIndex(
          (_data) => _data.uid === uid
        );
        if (itemIndex > -1) {
          state.items[patientIndex].data.splice(itemIndex, 1);
        }
        if (state.items[patientIndex].data.length === 0) {
          state.items.splice(patientIndex, 1);
        }
      }
    }
  }
});

export const { addToCart, removeFromCart, setCart } = cartSlice.actions;
export default cartSlice.reducer;

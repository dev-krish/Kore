import { configureStore } from "@reduxjs/toolkit";
import campaignReducer from "./slices/campaignSlice";
import profileReducer from "./slices/profileSlice";
import draftReducer from "./slices/draftSlice";

export const store = configureStore({
  reducer: {
    campaigns: campaignReducer,
    profile: profileReducer,
    drafts: draftReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

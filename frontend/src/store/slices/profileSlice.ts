import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { StudentProfile } from "@/types";
import { ProfileAPI } from "@/lib/api";

interface ProfileState {
  profile: StudentProfile | null;
  loading: boolean;
  error: string | null;
}

const initialState: ProfileState = {
  profile: null,
  loading: false,
  error: null,
};

export const fetchProfile = createAsyncThunk("profile/fetch", async () => {
  return await ProfileAPI.getMe();
});

export const saveProfile = createAsyncThunk("profile/save", async (data: Partial<StudentProfile>) => {
  return await ProfileAPI.updateMe(data);
});

export const profileSlice = createSlice({
  name: "profile",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchProfile.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.profile = action.payload;
      })
      .addCase(fetchProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to load profile";
      })
      .addCase(saveProfile.fulfilled, (state, action) => {
        state.profile = action.payload;
      });
  },
});

export default profileSlice.reducer;

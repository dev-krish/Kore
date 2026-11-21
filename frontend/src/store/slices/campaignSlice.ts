import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { Campaign } from "@/types";
import { CampaignAPI } from "@/lib/api";

interface CampaignState {
  campaigns: Campaign[];
  currentCampaign: Campaign | null;
  loading: boolean;
  error: string | null;
}

const initialState: CampaignState = {
  campaigns: [],
  currentCampaign: null,
  loading: false,
  error: null,
};

export const fetchCampaigns = createAsyncThunk("campaigns/fetchAll", async () => {
  return await CampaignAPI.list();
});

export const fetchCampaignById = createAsyncThunk("campaigns/fetchById", async (id: string) => {
  return await CampaignAPI.getById(id);
});

export const campaignSlice = createSlice({
  name: "campaigns",
  initialState,
  reducers: {
    setCurrentCampaign(state, action: PayloadAction<Campaign | null>) {
      state.currentCampaign = action.payload;
    },
    updateCampaignStatus(state, action: PayloadAction<{ id: string; status: any }>) {
      if (state.currentCampaign && state.currentCampaign._id === action.payload.id) {
        state.currentCampaign.status = action.payload.status;
      }
      const item = state.campaigns.find((c) => c._id === action.payload.id);
      if (item) {
        item.status = action.payload.status;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCampaigns.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCampaigns.fulfilled, (state, action) => {
        state.loading = false;
        state.campaigns = action.payload;
      })
      .addCase(fetchCampaigns.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to fetch campaigns";
      })
      .addCase(fetchCampaignById.fulfilled, (state, action) => {
        state.currentCampaign = action.payload;
      });
  },
});

export const { setCurrentCampaign, updateCampaignStatus } = campaignSlice.actions;
export default campaignSlice.reducer;

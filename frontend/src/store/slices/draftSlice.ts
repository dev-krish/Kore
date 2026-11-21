import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { EmailDraft } from "@/types";
import { DraftAPI } from "@/lib/api";

interface DraftState {
  drafts: EmailDraft[];
  selectedDraft: EmailDraft | null;
  loading: boolean;
  error: string | null;
}

const initialState: DraftState = {
  drafts: [],
  selectedDraft: null,
  loading: false,
  error: null,
};

export const fetchDrafts = createAsyncThunk(
  "drafts/fetch",
  async (params?: { campaignId?: string; status?: string }) => {
    return await DraftAPI.list(params);
  }
);

export const draftSlice = createSlice({
  name: "drafts",
  initialState,
  reducers: {
    setSelectedDraft(state, action: PayloadAction<EmailDraft | null>) {
      state.selectedDraft = action.payload;
    },
    updateDraftLocally(state, action: PayloadAction<EmailDraft>) {
      const idx = state.drafts.findIndex((d) => d._id === action.payload._id);
      if (idx !== -1) {
        state.drafts[idx] = action.payload;
      }
      if (state.selectedDraft && state.selectedDraft._id === action.payload._id) {
        state.selectedDraft = action.payload;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDrafts.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchDrafts.fulfilled, (state, action) => {
        state.loading = false;
        state.drafts = action.payload;
      })
      .addCase(fetchDrafts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to load drafts";
      });
  },
});

export const { setSelectedDraft, updateDraftLocally } = draftSlice.actions;
export default draftSlice.reducer;

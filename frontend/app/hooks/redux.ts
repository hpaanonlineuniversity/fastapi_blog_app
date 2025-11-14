// hooks/redux.ts - UPDATED VERSION
import { useDispatch, useSelector, useStore, TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from '../lib/store';

// ✅ Export the store instance for API interceptor access
export { store } from '../lib/store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
export const useAppStore = () => useStore<RootState>();
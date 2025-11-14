// lib/store.ts - UPDATED VERSION
import { configureStore } from '@reduxjs/toolkit';
import { persistReducer, persistStore } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import { combineReducers } from 'redux';
import userReducer from '../redux/user/userSlice';
import themeReducer from '../redux/theme/themeSlice';

const rootReducer = combineReducers({ 
  user: userReducer,
  theme: themeReducer,
});

const persistConfig = {
  key: 'root',
  version: 1,
  storage,
  whitelist: ['user', 'theme'], // ✅ Specify what to persist
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) => 
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// ✅ Make store globally available for API interceptor
if (typeof window !== 'undefined') {
  (window as any).__REDUX_STORE__ = store;
}
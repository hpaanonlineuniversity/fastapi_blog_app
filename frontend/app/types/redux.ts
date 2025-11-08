
// types/redux.ts
export interface RootState {
  user: {
    currentUser: {
      id: string;
      isAdmin: boolean;
    };
  };
}
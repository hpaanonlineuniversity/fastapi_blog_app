export interface DashboardTab {
  key: string;
  label: string;
  component: React.ComponentType;
}

export type TabType = 'profile' | 'posts' | 'users' | 'comments' | 'dash' | '';
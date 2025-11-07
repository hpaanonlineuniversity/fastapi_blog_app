'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import DashSidebar from '../components/DashSidebar';
import DashProfile from '../components/DashProfile';
//import DashPosts from '../components/DashPosts';
//import DashUsers from '../components/DashUsers';
//import DashComments from '../components/DashComments';
//import DashBoardMonitor from '../components/DashBoardMonitor';

export default function Dashboard() {
  const searchParams = useSearchParams();
  const [tab, setTab] = useState<string>('');
  
  useEffect(() => {
    const tabFromUrl = searchParams.get('tab');
    console.log(tabFromUrl);

    if (tabFromUrl) {
      setTab(tabFromUrl);
    }
  }, [searchParams]);

  return (
    <div className='min-h-screen flex flex-col md:flex-row'>
      <div className='md:w-56'>
        {/* Sidebar */}
        <DashSidebar />
      </div>

      {/* Main Content - Takes remaining space */}
      <div className='flex-1'>
        {/* profile... */}
        {tab === 'profile' && <DashProfile />}
 
      </div>
    </div>
  );
}
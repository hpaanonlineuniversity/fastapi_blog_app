'use client';

import { Sidebar, SidebarItem, SidebarItemGroup, SidebarItems } from "flowbite-react";
import {
    HiArrowSmRight,
    HiChartPie,
    HiUser,
    HiDocumentText,
    HiOutlineUserGroup,
    HiAnnotation,
} from 'react-icons/hi';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import { signOut } from '../redux/user/userSlice';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../lib/store';
import { apiInterceptor } from "../utils/apiInterceptor";

export default function DashSidebar() {
  const searchParams = useSearchParams();
  const dispatch = useDispatch();
  const { currentUser } = useSelector((state: RootState) => state.user);
  const [tab, setTab] = useState<string>('');
  const router = useRouter();

  useEffect(() => {
    const tabFromUrl = searchParams.get('tab');
    if (tabFromUrl) {
      setTab(tabFromUrl);
    }
  }, [searchParams]);

  const handleSignOut = async () => {
    try {
      const response = await apiInterceptor.request('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      console.log('Signout response status:', response.status);
      if (response.ok) {
        dispatch(signOut());
        router.push('/sign-in');
      }
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <Sidebar className='w-full md:w-56'>
      <SidebarItems>
        <SidebarItemGroup className='flex flex-col gap-1'>
          {currentUser && currentUser.isAdmin && (
            <Link href='/dashboard?tab=dash'>
              <SidebarItem
                active={tab === 'dash' || !tab}
                icon={HiChartPie}
                as='div'
              >
                Dashboard
              </SidebarItem>
            </Link>
          )}

          <Link href='/dashboard?tab=profile'>
            <SidebarItem
              active={tab === 'profile'}
              icon={HiUser}
              label={currentUser?.isAdmin ? 'Admin' : 'User'}
              labelColor='dark'
              as='div'
            >
              Profile
            </SidebarItem>
          </Link>

          {currentUser?.isAdmin && (
            <Link href='/dashboard?tab=posts'>
              <SidebarItem
                active={tab === 'posts'}
                icon={HiDocumentText}
                as='div'
              >
                Posts
              </SidebarItem>
            </Link>
          )}

          {currentUser?.isAdmin && (
            <>
              <Link href='/dashboard?tab=users'>
                <SidebarItem
                  active={tab === 'users'}
                  icon={HiOutlineUserGroup}
                  as='div'
                >
                  Users
                </SidebarItem>
              </Link>
              <Link href='/dashboard?tab=comments'>
                <SidebarItem
                  active={tab === 'comments'}
                  icon={HiAnnotation}
                  as='div'
                >
                  Comments
                </SidebarItem>
              </Link>
            </>
          )}

          <SidebarItem
            icon={HiArrowSmRight}
            className='cursor-pointer'
            onClick={handleSignOut}
          >
            Sign Out
          </SidebarItem>
        </SidebarItemGroup>
      </SidebarItems>
    </Sidebar>
  );
}
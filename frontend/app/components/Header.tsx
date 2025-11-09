'use client';

import { Avatar, Button, Dropdown, Navbar, TextInput } from 'flowbite-react';
import { DropdownDivider, DropdownHeader, DropdownItem } from "flowbite-react";
import { NavbarCollapse, NavbarLink, NavbarToggle } from "flowbite-react";
import { AiOutlineSearch } from 'react-icons/ai';
import { FaMoon, FaSun } from 'react-icons/fa';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useSelector, useDispatch } from 'react-redux';
import { signOut } from '../redux/user/userSlice';
import { toggleTheme } from '../redux/theme/themeSlice';
import { apiInterceptor } from '../utils/apiInterceptor';
import { RootState } from '../types/redux';

const Header = () => {
  const { currentUser } = useSelector((state: RootState) => state.user);
  const { theme } = useSelector((state: RootState) => state.theme);
  const router = useRouter();
  const pathname = usePathname();
  const dispatch = useDispatch();

  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const searchTermFromUrl = urlParams.get('searchTerm');

    if (searchTermFromUrl) {
      setSearchTerm(searchTermFromUrl);
    }
  }, [pathname]);

  const handleSignOut = async () => {
    try {
      await apiInterceptor.request('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
    } catch (error) {
      console.log('Signout API error:', error);
    } finally {
      // Always execute these steps regardless of API response
      dispatch(signOut());
      
      // Clear cookies manually
      document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      document.cookie = "refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      
      // Force redirect to sign-in
      window.location.href = '/sign-in';
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const urlParams = new URLSearchParams(window.location.search);
    
    if (searchTerm) {
      urlParams.set('searchTerm', searchTerm);
    } else {
      urlParams.delete('searchTerm');
    }
    
    const searchQuery = urlParams.toString();
    router.push(`/search?${searchQuery}`);
  };

  return (
    <>
      <Navbar className='border-b-2'>
        <Link
          href='/'
          className='self-center whitespace-nowrap text-sm sm:text-xl font-semibold dark:text-white'
        >
          <span className='px-2 py-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-lg text-white'>
            ဘားအံ&apos;s
          </span>
          Blog App
        </Link>

        {/* Rest of your Header JSX remains the same */}
        <div className='flex-1 max-w-lg mx-4'>
          <form 
            className='w-full' 
            onSubmit={handleSubmit}
          >
            <TextInput
              type='text'
              placeholder='Search articles...'
              rightIcon={AiOutlineSearch}
              className='hidden lg:inline rounded-full'
              size="md"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSubmit(e);
                }
              }}
            />
          </form>
        </div>

        <Button 
          className='w-12 h-10 lg:hidden' 
          color='gray' 
          pill
          onClick={handleSubmit}
        >
          <AiOutlineSearch />
        </Button>

        <NavbarCollapse>
          <NavbarLink as={Link} href='/' active={pathname === "/"}>
            Home
          </NavbarLink>
          <NavbarLink as={Link} href='/about' active={pathname === "/about"}>
            About
          </NavbarLink>
          <NavbarLink as={Link} href='/projects' active={pathname === "/projects"}>
            Projects
          </NavbarLink>
        </NavbarCollapse>

        <div className='flex gap-2 md:order-2'>
          <Button
            className='w-12 h-10 hidden sm:inline'
            color='gray'
            pill
            onClick={() => dispatch(toggleTheme())}
          >
            {theme === 'light' ? <FaSun /> : <FaMoon />}
          </Button>

          {currentUser ? (
            <Dropdown
              arrowIcon={false}
              inline
              label={
                <Avatar alt='user' img={currentUser.profilePicture} rounded />
              }
            >
              <DropdownHeader>
                <span className='block text-sm'>@{currentUser.username}</span>
                <span className='block text-sm font-medium truncate'>
                  {currentUser.email}
                </span>
              </DropdownHeader>

              <Link href={'/profile'}>
                <DropdownItem>Profile</DropdownItem>
              </Link>

              <Link href={'/dashboard?tab=profile'}>
                <DropdownItem>Dashboard</DropdownItem>
              </Link>

              <DropdownDivider />
              <DropdownItem onClick={handleSignOut}>Sign out</DropdownItem>
            </Dropdown>
          ) : (
            <Link href='/sign-in'>
              <Button color='purple' outline>
                Sign In
              </Button>
            </Link>
          )}          
        </div>

        <NavbarToggle />
      </Navbar>
    </>
  );
};

export default Header;
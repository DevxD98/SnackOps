import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { MessageSquare, Camera, Calendar, ShoppingCart, ChefHat } from 'lucide-react';

interface LayoutProps {
    children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
    const location = useLocation();

    const navItems = [
        { path: '/', icon: MessageSquare, label: 'Chat Chef' },
        { path: '/fridge', icon: Camera, label: 'Fridge Scanner' },
        { path: '/planner', icon: Calendar, label: 'Meal Planner' },
        { path: '/grocery', icon: ShoppingCart, label: 'Grocery List' },
    ];

    return (
        <div className="flex h-screen bg-[#F7F4EC]">
            {/* Sidebar */}
            <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
                <div className="p-6 flex items-center gap-3 border-b border-gray-100">
                    <div className="bg-orange-500 p-2 rounded-lg">
                        <ChefHat className="w-6 h-6 text-white" />
                    </div>
                    <h1 className="text-xl font-bold text-gray-800">ChefByte</h1>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${isActive
                                    ? 'bg-orange-50 text-orange-600 font-semibold shadow-sm'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                    }`}
                            >
                                <Icon className={`w-5 h-5 ${isActive ? 'text-orange-500' : 'text-gray-400'}`} />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>

                <div className="p-4 border-t border-gray-100">
                    <div className="bg-orange-50 rounded-xl p-4">
                        <p className="text-xs font-medium text-orange-800 mb-1">Pro Tip</p>
                        <p className="text-xs text-orange-600">
                            Upload a photo of your fridge to get instant recipe ideas!
                        </p>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto">
                <div className="max-w-5xl mx-auto p-8">
                    {children}
                </div>
            </main>
        </div>
    );
};

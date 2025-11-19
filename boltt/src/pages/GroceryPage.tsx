import React, { useState } from 'react';
import { ShoppingCart, Plus, Trash2, Check } from 'lucide-react';

interface GroceryItem {
    id: string;
    name: string;
    checked: boolean;
    category: string;
}

export const GroceryPage: React.FC = () => {
    const [items, setItems] = useState<GroceryItem[]>([
        { id: '1', name: 'Tomatoes', checked: false, category: 'Produce' },
        { id: '2', name: 'Onions', checked: true, category: 'Produce' },
        { id: '3', name: 'Rice', checked: false, category: 'Grains' },
        { id: '4', name: 'Chicken', checked: false, category: 'Meat' },
    ]);
    const [newItem, setNewItem] = useState('');

    const addItem = (e: React.FormEvent) => {
        e.preventDefault();
        if (!newItem.trim()) return;

        const item: GroceryItem = {
            id: Date.now().toString(),
            name: newItem.trim(),
            checked: false,
            category: 'Other',
        };

        setItems([...items, item]);
        setNewItem('');
    };

    const toggleItem = (id: string) => {
        setItems(items.map(item =>
            item.id === id ? { ...item, checked: !item.checked } : item
        ));
    };

    const deleteItem = (id: string) => {
        setItems(items.filter(item => item.id !== id));
    };

    return (
        <div className="max-w-3xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">Grocery List</h2>
                    <p className="text-gray-500 mt-1">Manage your shopping items</p>
                </div>
                <div className="bg-orange-100 text-orange-600 px-4 py-2 rounded-full font-medium">
                    {items.filter(i => !i.checked).length} items remaining
                </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-6 border-b border-gray-100 bg-gray-50">
                    <form onSubmit={addItem} className="flex gap-3">
                        <div className="relative flex-1">
                            <ShoppingCart className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                value={newItem}
                                onChange={(e) => setNewItem(e.target.value)}
                                placeholder="Add item (e.g., Milk, Eggs)..."
                                className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={!newItem.trim()}
                            className="bg-orange-500 text-white px-6 py-3 rounded-xl font-semibold hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                        >
                            <Plus className="w-5 h-5" />
                            Add
                        </button>
                    </form>
                </div>

                <div className="divide-y divide-gray-100">
                    {items.length === 0 ? (
                        <div className="p-12 text-center text-gray-400">
                            <ShoppingCart className="w-12 h-12 mx-auto mb-3 opacity-20" />
                            <p>Your list is empty</p>
                        </div>
                    ) : (
                        items.map((item) => (
                            <div
                                key={item.id}
                                className={`p-4 flex items-center justify-between group transition-colors ${item.checked ? 'bg-gray-50' : 'hover:bg-orange-50/30'
                                    }`}
                            >
                                <div className="flex items-center gap-4">
                                    <button
                                        onClick={() => toggleItem(item.id)}
                                        className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${item.checked
                                                ? 'bg-green-500 border-green-500 text-white'
                                                : 'border-gray-300 hover:border-orange-400'
                                            }`}
                                    >
                                        {item.checked && <Check className="w-4 h-4" />}
                                    </button>
                                    <span
                                        className={`text-lg ${item.checked ? 'text-gray-400 line-through' : 'text-gray-700'
                                            }`}
                                    >
                                        {item.name}
                                    </span>
                                </div>
                                <button
                                    onClick={() => deleteItem(item.id)}
                                    className="text-gray-400 hover:text-red-500 p-2 rounded-lg hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all"
                                >
                                    <Trash2 className="w-5 h-5" />
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

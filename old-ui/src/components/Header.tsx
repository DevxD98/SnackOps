import { ChefHat, Settings } from 'lucide-react';

interface HeaderProps {
  onOpenPreferences: () => void;
}

export function Header({ onOpenPreferences }: HeaderProps) {
  return (
    <header className="shadow-sm border-b-2" style={{ backgroundColor: '#FFFFFF', borderBottomColor: '#E8DFC8' }}>
      <div className="container mx-auto px-4 py-4 max-w-6xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg" style={{ backgroundColor: '#628141' }}>
              <ChefHat className="w-7 h-7" style={{ color: '#F7F4EC' }} strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-2xl font-bold" style={{ color: '#628141' }}>
                SnackOps
              </h1>
              <p className="text-sm" style={{ color: '#8B8674' }}>AI-Powered Meal Planning</p>
            </div>
          </div>

          <button
            onClick={onOpenPreferences}
            className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all border-2 font-medium"
            style={{
              backgroundColor: '#F7F4EC',
              borderColor: '#E8DFC8',
              color: '#5B532C',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#EFE9DB';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#F7F4EC';
            }}
          >
            <Settings className="w-4 h-4" />
            <span>Preferences</span>
          </button>
        </div>
      </div>
    </header>
  );
}

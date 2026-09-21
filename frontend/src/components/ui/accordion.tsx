'use client';

import * as React from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AccordionContextType {
  openValues: string[];
  toggleItem: (val: string) => void;
  multiple?: boolean;
}

const AccordionContext = React.createContext<AccordionContextType | undefined>(undefined);

export interface AccordionProps extends React.HTMLAttributes<HTMLDivElement> {
  multiple?: boolean;
  defaultValue?: string[] | string;
  value?: string[] | string;
  onValueChange?: (val: string[]) => void;
}

export const Accordion = React.forwardRef<HTMLDivElement, AccordionProps>(
  ({ multiple = true, defaultValue = [], value, onValueChange, className, children, ...props }, ref) => {
    const [internalValues, setInternalValues] = React.useState<string[]>(() => {
      if (defaultValue) {
        return Array.isArray(defaultValue) ? defaultValue : [defaultValue];
      }
      return [];
    });

    const isControlled = value !== undefined;
    const currentValues = isControlled
      ? Array.isArray(value)
        ? value
        : [value]
      : internalValues;

    const toggleItem = React.useCallback(
      (val: string) => {
        let next: string[];
        if (multiple) {
          next = currentValues.includes(val)
            ? currentValues.filter((v) => v !== val)
            : [...currentValues, val];
        } else {
          next = currentValues.includes(val) ? [] : [val];
        }

        if (!isControlled) {
          setInternalValues(next);
        }
        onValueChange?.(next);
      },
      [currentValues, multiple, isControlled, onValueChange]
    );

    return (
      <AccordionContext.Provider value={{ openValues: currentValues, toggleItem, multiple }}>
        <div ref={ref} className={cn('w-full border-t border-white/15', className)} {...props}>
          {children}
        </div>
      </AccordionContext.Provider>
    );
  }
);
Accordion.displayName = 'Accordion';

export interface AccordionItemProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string;
}

export const AccordionItem = React.forwardRef<HTMLDivElement, AccordionItemProps>(
  ({ value, className, children, ...props }, ref) => {
    const ctx = React.useContext(AccordionContext);
    const isOpen = ctx?.openValues.includes(value) ?? false;

    return (
      <div
        ref={ref}
        data-state={isOpen ? 'open' : 'closed'}
        className={cn(
          'border-b border-white/15 transition-all duration-200',
          className
        )}
        {...props}
      >
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child)) {
            return React.cloneElement(child as React.ReactElement<{ value?: string; isOpen?: boolean }>, {
              value,
              isOpen,
            });
          }
          return child;
        })}
      </div>
    );
  }
);
AccordionItem.displayName = 'AccordionItem';

export interface AccordionTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  value?: string;
  isOpen?: boolean;
}

export const AccordionTrigger = React.forwardRef<HTMLButtonElement, AccordionTriggerProps>(
  ({ value, isOpen, className, children, ...props }, ref) => {
    const ctx = React.useContext(AccordionContext);

    return (
      <button
        ref={ref}
        type="button"
        data-state={isOpen ? 'open' : 'closed'}
        onClick={() => value && ctx?.toggleItem(value)}
        className={cn(
          'flex w-full items-center justify-between py-6 sm:py-7 text-left font-extrabold text-xl sm:text-2xl lg:text-3xl text-white hover:text-amber-300 transition-colors select-none cursor-pointer group',
          className
        )}
        {...props}
      >
        <span className="pr-4">{children}</span>
        <ChevronDown
          className={cn(
            'h-6 w-6 sm:h-7 sm:w-7 shrink-0 transition-transform duration-300 text-stone-400 group-hover:text-amber-300',
            isOpen && 'rotate-180 text-amber-300'
          )}
        />
      </button>
    );
  }
);
AccordionTrigger.displayName = 'AccordionTrigger';

export interface AccordionContentProps extends React.HTMLAttributes<HTMLDivElement> {
  isOpen?: boolean;
}

export const AccordionContent = React.forwardRef<HTMLDivElement, AccordionContentProps>(
  ({ isOpen, className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        data-state={isOpen ? 'open' : 'closed'}
        className={cn(
          'grid transition-all duration-300 ease-in-out',
          isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0 pointer-events-none'
        )}
      >
        <div className="overflow-hidden">
          <div className={cn('pb-6 pt-1 text-stone-200 leading-relaxed text-sm sm:text-base', className)} {...props}>
            {children}
          </div>
        </div>
      </div>
    );
  }
);
AccordionContent.displayName = 'AccordionContent';

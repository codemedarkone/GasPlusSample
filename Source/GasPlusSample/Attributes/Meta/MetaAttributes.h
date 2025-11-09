#pragma once

#include "CoreMinimal.h"

#if __has_include("UObject/NameTypes.h")
#include "UObject/NameTypes.h"
#include "Containers/UnrealString.h"
#endif

#if __has_include("Containers/Map.h")
#include "Containers/Map.h"
#endif

#if !__has_include("UObject/NameTypes.h")
#include <string>
#endif

#if !__has_include("Containers/Map.h")
#include <map>
#include <stdexcept>
#endif

#ifndef TEXT
#define TEXT(x) x
#endif

namespace GasPlusSample::Attributes::Meta
{
    #if __has_include("UObject/NameTypes.h")
    using FMetaRegistryName = FName;
    using FMetaRegistryString = FString;
    #else
    struct FMetaRegistryName
    {
        FMetaRegistryName() = default;

        explicit FMetaRegistryName(const char* InName)
            : Value(InName ? InName : "")
        {
        }

        bool IsNone() const
        {
            return Value.empty();
        }

        bool operator==(const FMetaRegistryName& Other) const
        {
            return Value == Other.Value;
        }

        bool operator!=(const FMetaRegistryName& Other) const
        {
            return !(*this == Other);
        }

        std::string Value;
    };

    inline bool operator<(const FMetaRegistryName& Lhs, const FMetaRegistryName& Rhs)
    {
        return Lhs.Value < Rhs.Value;
    }

    using FMetaRegistryString = std::string;
    #endif

    #if __has_include("Containers/Map.h")
    template <typename KeyType, typename ValueType>
    using TMetaRegistryMap = TMap<KeyType, ValueType>;
    #else
    template <typename KeyType, typename ValueType>
    class TMetaRegistryMap
    {
    public:
        bool Contains(const KeyType& Key) const
        {
            return Storage.find(Key) != Storage.end();
        }

        void Add(const KeyType& Key, const ValueType& Value)
        {
            Storage[Key] = Value;
        }

        const ValueType* Find(const KeyType& Key) const
        {
            auto It = Storage.find(Key);
            if (It == Storage.end())
            {
                return nullptr;
            }
            return &It->second;
        }

        ValueType* Find(const KeyType& Key)
        {
            auto It = Storage.find(Key);
            if (It == Storage.end())
            {
                return nullptr;
            }
            return &It->second;
        }

        const ValueType& FindChecked(const KeyType& Key) const
        {
            auto It = Storage.find(Key);
            if (It == Storage.end())
            {
                throw std::out_of_range("Key not found in TMetaRegistryMap");
            }
            return It->second;
        }

    private:
        std::map<KeyType, ValueType> Storage;
    };
    #endif

    struct GASPLUSSAMPLE_API FMetaAttributeDefinition
    {
        FMetaAttributeDefinition() = default;

        FMetaAttributeDefinition(
            const FMetaRegistryName& InRegistryName,
            const FMetaRegistryName& InBackingAttributeName,
            const FMetaRegistryString& InDescription);

        FMetaRegistryName RegistryName;
        FMetaRegistryName BackingAttributeName;
        FMetaRegistryString Description;
    };

    class GASPLUSSAMPLE_API FMetaAttributesRegistry
    {
    public:
        static const FMetaAttributesRegistry& Get();
        static void RegisterEditorExtension(const FMetaAttributeDefinition& Definition);

        const FMetaAttributeDefinition& GetDamage() const;
        const FMetaAttributeDefinition& GetHeal() const;
        const FMetaAttributeDefinition& GetShieldDelta() const;

        const TMetaRegistryMap<FMetaRegistryName, FMetaAttributeDefinition>& GetDefinitions() const;
        const FMetaAttributeDefinition* FindDefinition(const FMetaRegistryName& RegistryName) const;

    private:
        FMetaAttributesRegistry();
        void Register(const FMetaAttributeDefinition& Definition);

        static const FMetaRegistryName DamageKey;
        static const FMetaRegistryName HealKey;
        static const FMetaRegistryName ShieldDeltaKey;

        TMetaRegistryMap<FMetaRegistryName, FMetaAttributeDefinition> Definitions;
    };
}
